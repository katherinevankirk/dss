import numpy as np
from dataclasses import dataclass


# --------------------------------- DSS DATA CLASS CONFIGURATION ------------------------------------- #



@dataclass
class DSSConfig:
    N: int                            # each Pauli string has length N
    depth: int                        # the maximum allowed depth of the measurement circuit
    eta: float                        # a noise-tolerance hyperparameter (often set as ε²) controlling what is prioritized in optimization
    max_num_measurements: int         # the maxium number of measurements you could make
    measurements_per_observable: int  # the cap for how often each observable is measured
    pauli_strings_to_learn: list[str] # list of Pauli strings (in str form) we want to estimate
    pauli_masks: np.ndarray           # array of Pauli strings we want to estimate (in boolean form - True for XYZ, False for I)
    weights: list[float]              # (optional) list of one float per Pauli string, indicating relative importance of each Pauli string



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


def build_config_from_file(pauli_filepath: str, weights_filepath: str, N: int, depth: int, eta: float, max_num_measurements: int, measurements_per_observable: int) -> DSSConfig:
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


    if max_num_measurements is None:
        max_num_measurements = len(pauli_strings) * measurements_per_observable

    return DSSConfig(
        N=N,
        depth=depth,
        eta=eta,
        max_num_measurements=max_num_measurements,
        measurements_per_observable=measurements_per_observable,
        pauli_strings_to_learn=pauli_strings_to_learn,
        pauli_masks=pauli_masks,
        weights=weights
    )
