import numpy as np
from dataclasses import dataclass


# --------------------------------- DSS DATA CLASS CONFIGURATION ------------------------------------- #



@dataclass
class DSSConfig:
    N: int
    depth: int
    eta: float
    total_measurements: int
    measurements_per_observable: int
    pauli_strings_to_learn: list[str]
    pauli_masks: np.ndarray
    weights: list[float]



def process_strings_to_masks(pauli_str_list):
    mask_list = []
    for p in pauli_str_list:
        this_mask = []
        for site in list(p):
            if site == 'I':
                this_mask.append(0)
            if site == 'X':
                this_mask.append(1)
            if site == 'Y':
                this_mask.append(2)
            if site == 'Z':
                this_mask.append(3)
        mask_list.append(this_mask)
    
    return np.array(mask_list)


def load_pauli_strings_from_file(filepath: str) -> list[str]:
    """Load a list of Pauli strings from a text file."""
    with open(filepath, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def load_weights_from_file(filepath: str) -> list[float]:
    """
    Load a list of float weights from a text file.
    
    Each line in the file should contain a single float value.
    Blank lines are ignored.
    """
    with open(filepath, 'r') as f:
        return [float(line.strip()) for line in f if line.strip()]


def build_config_from_file(pauli_filepath: str, weights_filepath: str, N: int, depth: int, eta: float, total_measurements: int, measurements_per_observable: int) -> DSSConfig:
    # Pauli strings we want to learn
    pauli_data = load_pauli_strings_from_file(pauli_filepath)
    pauli_strings_to_learn = process_strings_to_masks(pauli_data)
    pauli_masks = pauli_strings_to_learn.astype(bool) 

    # Option to weight the relative importance of the Paulis
    if weights_filepath is None:
        weights = [1.0] * len(pauli_masks)
    else: 
        weights = load_weights_from_file(weights_filepath)
    assert(len(weights) == len(pauli_masks))


    if total_measurements is None:
        total_measurements = len(pauli_strings) * measurements_per_observable

    return DSSConfig(
        N=N,
        depth=depth,
        eta=eta,
        total_measurements=total_measurements,
        measurements_per_observable=measurements_per_observable,
        pauli_strings_to_learn=pauli_strings_to_learn,
        pauli_masks=pauli_masks,
        weights=weights
    )