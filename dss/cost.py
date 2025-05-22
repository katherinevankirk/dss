
import numpy as np
import math


from dss.circuit import make_twrld_sig_twoq_set, initial_state_sig
from dss.tensor_contractions import dressed_gates_contract, dress_twoq_gates




# -------------------------------------- DSS COST HELPER FUNCTIONS --------------------------------------- #




# === Pauli Weight Calculations ===

twsig_id, twsig_cx, twsig_sw, twsig_u2 = make_twrld_sig_twoq_set()



def calculate_weight_structure(N, mask, depth, gate_config,):
    """
    For a given measurement circuit, specified by the two qubit gates (gate_config) and single qubit gates (single_qubit_config), 
    calculate the probability of learning a given Pauli string (pauli_mask). 

    Args:
        N (Int): number of qubits
        mask (Bool List): whether it is identity or non-identity in Pauli operator
        depth (Int): number of layers of gates
        gate_config (2D array of Int): dim(gate_config)=(depth,N//2) where each element is 0,1,2
            0=>identity, 1=>CNOT, 2=>swap
    
    Returns:
        weight (Float): Pauli weight, i.e. float in [0,1] that gives probability of learning a given Pauli string with specified circuit
    """

    twrld_sig_twoq_dict = {0:twsig_id, 1:twsig_cx, 2:twsig_sw, 3:twsig_u2 }

    gate_config_full = [[ twrld_sig_twoq_dict[g] for g in layer] for layer in gate_config ]
    state = initial_state_sig(np.asarray(mask, dtype=bool), N)

    return dressed_gates_contract(N,depth,state,gate_config_full,2)


def calculate_weight_single_qubit(N, pauli_mask, single_qubit_config, gate_config):
    """
    For a given measurement circuit, specified by the two qubit gates (gate_config) and single qubit gates (single_qubit_config), 
    calculate the probability of learning a given Pauli string (pauli_mask). 
    
    Args:
        N (Int): number of qubits
        pauli_mask (list of Ints): Pauli string to learn (0:I, 1:X, 2:Y, 3:Z)
        single_qubit_config (list of Int): the single qubit gates for this measurement 
        gate_config (2D array): the chosen structure (ie. two qubit gates) for this measurement
    
    Returns:
        weight (Float): Pauli weight, i.e. float in [0,1] that gives probability of learning a given Pauli string with specified circuit
    """

    # absorb all single-qubit gates into the two-qubit gates
    depth = len(gate_config)
    dressed_gates= dress_twoq_gates(gate_config, single_qubit_config.reshape((depth + 1, N)))
    
    # contract the two qubit gates
    state = [[i==p for i in range(4)]for p in pauli_mask]
    return dressed_gates_contract(N,depth,state,dressed_gates,4)

def weight_of_all_Paulis(N, single_qubit_config, gate_config, pauli_strings_to_learn):
    """
    For a given measurement circuit, specified by the two qubit gates (gate_config) and single qubit gates (single_qubit_config), 
    calculate the probability of learning each Pauli string we care about.
    
    Args:
        N (Int): number of qubits
        single_qubit_config (list of Int): the single qubit gates for this measurement 
        gate_config (2D array): the chosen structure (ie. two qubit gates) for this measurement
    
    Returns:
        List of floats in [0,1] that give probabilities of earning desired Pauli strings 
    """

    return [calculate_weight_single_qubit(N, pauli_mask, single_qubit_config, gate_config) for pauli_mask in pauli_strings_to_learn]





# === Cost Functions ===


def confidence_cost_function_structure(N, depth, eta, total_measurements, num_of_measurements_so_far, structure_config, pauli_masks, count_hits, structure_database, weight, num_of_measurements_per_observable):
    """
    For a given measurement circuit, calculate the COST function. 

    Args:
        num_of_measurements_so_far (Int): the number of measurements we have derandomized already
        structure_config (2D array): the chosen structure (ie. two qubit gates) for this measurement
                Note: all single qubit gates assumed to be still random in the current measurement 
        count_hits (list of Ints): number of times each Pauli has been measured by previous measurements
        weight (list of Floats): None or a list of coefficients for each observable
                 None -- neglect this parameter
                 a list -- modify the number of measurements for each observable by the corresponding weight
        num_of_measurements_per_observable (Int): int for the number of measurements per observable
    
    Returns:
        COST function for learning the given Pauli strings with current set of measurement circuits
    """

    # UNKNOWN FUTURE MEASUREMENTS:  use random clifford rotations
    random_config = 3* np.ones((depth,N//2)) #unknown future measurements 
    random_config_weights = structure_database[random_config.tobytes()]
    
    # THIS CURRENT MEASUREMENT WE ARE DERANDOMIZING:
    structure_config_weights = []
    if structure_config.tobytes() in structure_database.keys(): 
        structure_config_weights = structure_database[structure_config.tobytes()]
    else: 
        for l in range(len(pauli_masks)): 
            structure_config_weights.append( calculate_weight_structure(N, pauli_masks[l], depth, structure_config) )
        structure_database[structure_config.tobytes()] = structure_config_weights
    
    # CALCULATE COST FUNCTION
    cost = 0  
    for l in range(len(pauli_masks)):

        if count_hits[l] >= math.floor(weight[l] * num_of_measurements_per_observable):
            continue

        nu = 1 - math.exp(-eta / 2)

        # Calculate COST contributions from the past measurements ("fixed"), the current measurement ("partial"), and the unknown 
        # future measurements ("randomized")        
        cost_l_fixed = math.exp( (-eta / 2) * count_hits[l])
        cost_l_paritial = ( 1 - nu * structure_config_weights[l])
        cost_l_randomized = ( 1 - nu * random_config_weights[l])**(total_measurements - num_of_measurements_so_far-1)

        cost += weight[l]*(cost_l_fixed * cost_l_paritial * cost_l_randomized)
    
    return cost




def confidence_cost_function_single_qubit(N, depth, eta, total_measurements, num_of_measurements_so_far, column_test, gate_config, pauli_strings_to_learn, pauli_masks, count_hits, structure_database, single_qubit_database, weight, num_of_measurements_per_observable):
    """
    For a given measurement circuit, calculate the COST function. 

    Args:
        num_of_measurements_so_far (Int): the number of measurements we have derandomized already
        column_test (list of Int): the single qubit gates we're testing for this measurement
        gate_config (2D array): the chosen structure (ie. two qubit gates) for this measurement
        count_hits (list of Ints): number of times each Pauli has been measured by previous measurements
        weight (list of Floats): None or a list of coefficients for each observable
                 None -- neglect this parameter
                 a list -- modify the number of measurements for each observable by the corresponding weight
        num_of_measurements_per_observable (Int): int for the number of measurements per observable
    
    Returns:
        COST function for learning the given Pauli strings with current set of measurement circuits
    """

    # UNKNOWN FUTURE MEASUREMENTS:  use random clifford rotations
    random_config = 3* np.ones((depth,N//2)) 
    random_config_weights = structure_database[random_config.tobytes()]
    
    # THIS CURRENT MEASUREMENT WE ARE DERANDOMIZING: 
    fully_fixed_config_weights = []

    this_key = np.concatenate((column_test,gate_config.flatten()))
    this_key = this_key.tobytes()

    # ---> Option 1. We have seen this_key before and therefore it is in the database
    if this_key in single_qubit_database.keys(): 
        fully_fixed_config_weights = single_qubit_database[this_key]
    
    # ---> Option 2. We have *NOT* seen this_key before and therefore we must add it to the database
    else: 
        for l in range(len(pauli_masks)): 
            fully_fixed_config_weights.append( calculate_weight_single_qubit(N, pauli_strings_to_learn[l], column_test, gate_config) )
        single_qubit_database[this_key] = fully_fixed_config_weights
    
    # CALCULATE COST FUNCTION
    cost = 0   
    for l in range(len(pauli_masks)): #iterate through observables
        
        if count_hits[l] >= math.floor(weight[l] * num_of_measurements_per_observable):
            continue

        nu = 1 - math.exp(-eta / 2)

        # Calculate COST contributions from the past measurements ("fixed"), the current measurement ("partial"), and the unknown 
        # future measurements ("randomized")
        cost_l_fixed = math.exp( (-eta / 2) * count_hits[l])
        cost_l_paritial = ( 1 - nu * fully_fixed_config_weights[l])
        cost_l_randomized = ( 1 - nu * random_config_weights[l])**(total_measurements - num_of_measurements_so_far-1)
        
        cost += weight[l]*(cost_l_fixed * cost_l_paritial * cost_l_randomized)       

    return cost