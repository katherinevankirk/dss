"""
This module defines tensor-based quantum gates,
measurement and optimization routines for simulating
parameterized quantum circuits using MPO-like structures.

# GATE CONVENTION : The result of this will be a list of single qubit rotations. They are applied in order from front to back, 
# following the opposite order of the two qubit gate convention. (First gate in array is upper left near the first Pauli site, second
# gate is one qubit down, etc. Then you eventually go to next layer towards the measurements.) In circuit format, the output will be
# the transpose of all single qubit gates you defined.

"""

import argparse
import numpy as np
import time

from dss.config import build_config_from_file
from dss.derandomization import full_derandomization


# === Entry Point ===
def main() -> None:
    parser = argparse.ArgumentParser(description="Run DSS algorithm on a Pauli string dataset.")

    # Add CLI arguments
    parser.add_argument("--N", type=int, default=8, help="Number of qubits")
    parser.add_argument("--depth", type=int, default=3, help="Circuit depth")
    parser.add_argument("--eta", type=float, default=0.9, help="Eta hyperparameter (usually epsilon^2)")
    parser.add_argument("--total_measurements", type=int, default=100, help="Total number of measurements")
    parser.add_argument("--measurements_per_observable", type=int, default=100, help="Measurements per observable")
    parser.add_argument("--pauli_file", type=str, required=True, help="Path to Pauli strings text file")
    parser.add_argument("--weights_file", type=str, default=None, help="Path to Weights text file")

    args = parser.parse_args()

    # Build config using parsed CLI args 
    config = build_config_from_file(
        pauli_filepath=args.pauli_file,
        weights_filepath=args.weights_file,
        N=args.N,
        depth=args.depth,
        eta=args.eta,
        total_measurements=args.total_measurements-1,
        measurements_per_observable=args.measurements_per_observable
    )

    # Run derandomization
    derandtime = time.time()
    mmts_struc, mmts_rots, mmts_counts = full_derandomization(config)
    print('\nTOTAL TIME REQ FOR DERANDOMIZATION:', time.time() - derandtime, 'secs')


if __name__ == '__main__':
    main()
