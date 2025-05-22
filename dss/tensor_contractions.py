
from functools import reduce
import numpy as np

from dss.gates import identity_gate, swap_gate, cnot_gate, u2_gate
from dss.gates import gate1, gate2, gate3, gate4, gate5, gate6, random_singleq_gate




# ---------------------------- HELPER FUNCTIONS FOR TENSOR NETWORK CONTRACTIONS -------------------------- #




# === Tensor Network Contraction Logic ===

def dressed_gates_contract(N, depth, state, gate_config_full, bond_dim_factor):
    """
    Contract a tensor network to compute the Pauli weight of a given Pauli string 
    under a parameterized measurement circuit.

    Args:
        N (int): Number of qubits.
        depth (int): Number of two-qubit gate layers.
        state (np.ndarray): Array of shape (N, 2) encoding identity ([1, 0]) or non-identity ([0, 1]) per qubit.
        gate_config_full (np.ndarray): Shape (depth, N//2, ...), with entries 0 (I), 1 (CNOT), or 2 (SWAP).
        bond_dim_factor (int): Representation size. 
            - 2: Identity vs Non-Identity.
            - 4: Full Pauli support (I, X, Y, Z).

    Returns:
        float: Pauli weight for the given circuit and Pauli string.
    """

    def pair_input_states(state, N, depth_parity):
        """Group input qubit states into pairs, offset by parity."""
        offset = int(not depth_parity)
        return [
            [state[(2 * i + offset) % N], state[(2 * i + 1 + offset) % N]]
            for i in range(N // 2)
        ]

    def apply_initial_gates(paired_states, gate_layer, depth_parity):
        """Contract input states with the first layer of gates."""
        contracted = [
            np.einsum('a,b,abkl->kl', s1, s2, gate)
            for (s1, s2), gate in zip(paired_states, gate_layer)
        ]
        if depth_parity == 0:
            contracted = [np.transpose(mat) for mat in contracted]
        return contracted

    def reshape_for_temporal_contraction(matrices, bond_dim, depth_parity):
        """Add temporal legs to enable MPS-style vertical contraction."""
        if depth_parity == 0:
            new_shape = [1, bond_dim, bond_dim]
        else:
            new_shape = [bond_dim, 1, bond_dim]
        return [mat.reshape(new_shape) for mat in matrices]

    def get_measurement_tensor(bond_dim):
        """Return the measurement tensor vector depending on encoding."""
        if bond_dim == 4:
            return [1, 0, 0, 1]
        elif bond_dim == 2:
            return [1, 1 / 3]
        else:
            raise ValueError("Unsupported bond dimension factor")

    def apply_middle_layers(tensor_chain, gate_config, bond_dim):
        """Iteratively contract all internal layers except first/last."""
        for d in range(depth - 2, 0, -1):
            layer = gate_config[d]
            parity = d % 2
            curr_shape = (
                len(tensor_chain),
                len(tensor_chain[0]),
                len(tensor_chain[0][0]),
                len(tensor_chain[0][0][0]),
            )
            if parity == 0:
                tensor_chain = np.einsum(
                    'sijk,sakcd->siacjd', tensor_chain, layer
                ).reshape([curr_shape[0], curr_shape[1] * bond_dim**2, curr_shape[2], bond_dim])
            elif parity == 1:
                tensor_chain = np.einsum(
                    'sijk,skbcd->sijbdc', tensor_chain, layer
                ).reshape([curr_shape[0], curr_shape[1], curr_shape[2] * bond_dim**2, bond_dim])
            else:
                raise ValueError("Invalid layer parity")
        return tensor_chain

    def apply_final_layer(tensor_chain, final_gates, meas_tensor, bond_dim):
        """Contract the last gate layer with the measurement tensor."""
        dressed_gates = [
            np.einsum('k,l,ijkl->ij', meas_tensor, meas_tensor, g)
            for g in final_gates
        ]
        curr_shape = (
            len(tensor_chain),
            len(tensor_chain[0]),
            len(tensor_chain[0][0]),
            len(tensor_chain[0][0][0]),
        )
        contracted = np.einsum(
            'sijk,sak->siaj', tensor_chain, dressed_gates
        ).reshape([curr_shape[0], curr_shape[1] * bond_dim, curr_shape[2]])
        return contracted

    

    # ------------------ Main Logic ------------------ #

    depth_parity = depth % 2
    paired_input_states = pair_input_states(state, N, depth_parity)
    first_layer_gates = gate_config_full[-1]
    
    tensor_chain = apply_initial_gates(paired_input_states, first_layer_gates, depth_parity)
    tensor_chain = reshape_for_temporal_contraction(tensor_chain, bond_dim_factor, depth_parity)
    meas_tensor = get_measurement_tensor(bond_dim_factor)

    if depth == 1:
        tensor_chain = [mat.reshape([bond_dim_factor, bond_dim_factor]) for mat in tensor_chain]
        return np.prod(np.einsum('a,b,sab->s', meas_tensor, meas_tensor, tensor_chain))

    tensor_chain = apply_middle_layers(tensor_chain, gate_config_full, bond_dim_factor)
    final_layer_gates = gate_config_full[0]
    tensor_chain = apply_final_layer(tensor_chain, final_layer_gates, meas_tensor, bond_dim_factor)

    return np.trace(reduce(np.matmul, tensor_chain))




def dress_twoq_gates(gate_config, single_qubit_config):
    """
    Dress two-qubit gates by contracting with adjacent single-qubit gates according 
    to specified configurations, producing dressed two-qubit gate tensors.

    Args:
        gate_config (list[list[int]]): Depth x #two-qubit-gates per layer, with each
            entry encoding a two-qubit gate index.
        single_qubit_config (np.ndarray): Depth x #single-qubit-gates per layer,
            specifying single-qubit gate indices.

    Returns:
        list[list[np.ndarray]]: Nested list of dressed two-qubit gate tensors, shaped
            by (depth, #two-qubit gates per layer), where each tensor has shape (4,4,4,4).
    """

    def get_two_qubit_gate_dict():
        """Return mapping from gate index to two-qubit gate tensor."""
        return {
            0: identity_gate(),
            1: cnot_gate(),
            2: swap_gate(),
            3: u2_gate(),
        }

    def get_single_qubit_gate_dict():
        """Return mapping from gate index to single-qubit gate tensor."""
        return {
            0: random_singleq_gate(),
            1: gate1(),
            2: gate2(),
            3: gate3(),
            4: gate4(),
            5: gate5(),
            6: gate6(),
        }

    def reorder_single_qubit_config(s_config):
        """
        Reorder single-qubit config array so it aligns with two-qubit gate convention.
        This includes flipping the config depth-wise and applying a parity-dependent roll.
        """
        last_index = len(s_config) - 1
        flipped = np.flip(s_config, axis=0)
        return [
            np.roll(layer, -((i + (i == last_index)) % 2))
            for i, layer in enumerate(flipped)
        ]



    # ------------------ Main logic ------------------ #

    twoq_gate_dict = get_two_qubit_gate_dict()
    single_gate_dict = get_single_qubit_gate_dict()
    canonical_single_config = reorder_single_qubit_config(single_qubit_config)

    # Convert gate indices to actual gate tensors for all layers
    single_gates_full = [
        [single_gate_dict[g] for g in layer]
        for layer in canonical_single_config
    ]
    twoq_gates_full = [
        [twoq_gate_dict[g] for g in layer]
        for layer in gate_config
    ]

    dressed_gates = [
        [
            np.einsum('ak,bl,ijab->ijkl', s_layer[2 * i], s_layer[2 * i + 1], d_layer[i])
            for i in range(len(d_layer))
        ]
        for s_layer, d_layer in zip(single_gates_full[:-1], twoq_gates_full)
    ]

    last_s_layer = single_gates_full[-1]
    last_dressed_layer = dressed_gates[-1]
    dressed_gates[-1] = [
        np.einsum('ia,jb,abkl->ijkl', last_s_layer[2 * i], last_s_layer[2 * i + 1], last_dressed_layer[i])
        for i in range(len(last_dressed_layer))
    ]

    return dressed_gates