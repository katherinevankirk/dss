"""
This code runs the DSS algorithm using the DSS package. Our
package uses tensors to represent quantum gates, measurement, 
and the desired Pauli strings. It returns a set of low-depth 
measurements that one should make on their quantum computer
to efficiently learn the specified Pauli strings. 

GATE CONVENTION : The result of this algorithm will be a list of two-qubit (mmts_struc) and single-qubit (mmts_rots) rotations. They 
are applied in order from back to front (two-qubit rotations) and from front to back (single-qubit rotations). For example, for the
single-qubit rotations, the first gate in the array is the upper-left-most gate near the first Pauli site. The second gate is one 
qubit down, etc. This continues for each gate in this layer, and then for the next layer, you again start at the top. 

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
    parser.add_argument("--max_num_measurements", type=int, default=100, help="Total number of measurements")
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
        max_num_measurements=args.max_num_measurements-1,
        measurements_per_observable=args.measurements_per_observable
    )

    # Run derandomization
    derandtime = time.time()
    mmts_struc, mmts_rots, mmts_counts = full_derandomization(config)
    print('\nTOTAL TIME REQ FOR DERANDOMIZATION:', time.time() - derandtime, 'secs')


if __name__ == '__main__':
    main()
