# DSS: Derandomized Shallow Shadows

**A framework for efficiently estimating Pauli string observables with bounded-depth measurements**  


[![Unitary Fund](https://img.shields.io/badge/Supported%20By-UNITARY%20FOUNDATION-brightgreen.svg?style=for-the-badge)](http://unitary.fund)

[![Python](https://img.shields.io/badge/python-3.8+-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/katherinevankirk/dss)](LICENSE)


---

## 🔍 About

This project implements methods from:

> Katherine Van Kirk, Christian Kokail, Jonathan Kunjummen, Hong-Ye Hu, Yanting Teng, Madelyn Cain, Jacob Taylor, Susanne F. Yelin, Hannes Pichler, and Mikhail Lukin. *Derandomized shallow shadows: Efficient Pauli learning with bounded-depth circuits*.  
> [arXiv:2412.18973](https://arxiv.org/abs/2412.18973)

It provides tools to run the derandomized shallow shadows (DSS) algorithm, which optimizes shallow measurement circuits for learning a given set of Pauli strings. The algorithm specifies some set of measurement circuits, which rotate into the desired measurement bases. Crucially, these measurement circuits each contain at most depth $d$ layers of two qubit gates, and the algorithm determines these circuits by derandomizing shallow shadows. Exploiting tensor network techniques that mimic classical Markovian processes, our algorithm optimizes shallow circuits to maximize the probability of learning the given set of Pauli strings. We find effective, shallow circuits by selecting circuits with high probability of learning the Pauli strings. 

---

## 📦 Features

- 🧮 Homemade, special-purpose tensor network contraction functions
- 📉 Compute cost functions based on probability of learning a set of Pauli strings
- 🎯 Optimize short-depth measurement circuits using derandomization
- 🧰 Configure derandomization procedure via a central `DSSConfig`
- 💻 Command-line and Python API interfaces
- 🧩 Only dependency is Numpy

---

## 🛠️ Installation

Clone and install from [GitHub](https://github.com/katherinevankirk/dss):

```bash
git clone https://github.com/katherinevankirk/dss.git
cd dss
pip install -e .
```

---

## 🚀 Usage

DSS can be run via the command line or directly as a Python library. We include two example Pauli string files for demonstration:
- 📄 `pauli_strings_30.txt`: a realistic workload of 30 unique 8-qubit Pauli strings.
- 📄 `pauli_strings_bell.txt`: a minimal test case of 3 commuting Pauli strings, diagonal in the Bell basis.

The DSS algorithm will terminate when either:
1. The total number of measurements is reached, **or**
2. Each Pauli observable is measured `measurements_per_observable` times.

   

### Command-Line

```bash
python run_dss.py \
    --N 8 \
    --depth 3 \
    --eta 0.9 \
    --total_measurements 100 \
    --pauli_file pauli_strings_30.txt
```

### Python API

```python
from dss.config import build_config_from_file
from dss.derandomization import full_derandomization

config = build_config_from_file(
    pauli_filepath="pauli_strings_bell.txt",   # all Pauli strings should be stored in a .txt file with one string per line, each of length N
    weights_filepath=args."weights.txt",       # (optional) create a file with one float per line, corresponding to relative importance of each Pauli string
    N=8,                                       # the length of the Pauli strings (i.e., number of qubits)
    depth=3,                                   # the maximum allowed depth of the measurement circuit
    eta=0.9,                                   # a noise-tolerance hyperparameter (often set as ε²)
    total_measurements=100,                    # the number of total measurements
    measurements_per_observable=100            # the cap for how often each observable is measured
)
results = full_derandomization(config)
```


---

## 🧱 Project Structure

```
dss/
├── config.py                  # DSSConfig, file loading
├── gates.py                   # Quantum gate definitions
├── circuit.py                 # Dressing, single/two-qubit gate processing
├── tensor_constractions.py    # State prep, twirling, contractions
├── cost.py                    # Cost and weight functions
├── derandomization.py         # Optimization logic
run_dss.py                     # Command-line entry point
```

---

## 🧠 Background: How the DSS Algorithm Works

The **Derandomized Shallow Shadows (DSS)** algorithm provides an efficient strategy for learning Pauli observables using **bounded-depth quantum circuits**. In many quantum applications (e.g. chemistry, simulation, phase recognition), we must **estimate expectation values of many Pauli strings**. However, directly estimating each Pauli string is inefficient, grouping strategies require large circuit depth, and while shallow shadow schemes are low depth, they are not tailored to the specific Pauli learning problem. Indeed usually we know ahead of time what Paulis we want to estimate in our experiment. DSS avoids randomization by **systematically selecting measurement circuits** that maximize Pauli learnability under depth constraints.


#### 💡 DSS Strategy

At a high level, the algorithm derandomizes each measurement with the following steps:
1. Fixes a shallow **ansatz** a depth-`d` quantum circuit with N qubits
2. Chooses **2-qubit gates** from a discrete set (e.g., CNOT, SWAP)
3. Chooses **1-qubit gates** from a discrete set (e.g., H, S)
4. Returns the final measurement circuit

<img src="/doc/derand_scheme.png" alt="Alt text" height="220" width="900">

This mimics a **greedy walk through the configuration space**, favoring setups that are globally effective. DSS efficiently evaluates each candidate circuit using **tensor network methods** that computes the expected information gain from that layout. In other words, the DSS algorithm scores circuits based on the **probability of learning all Pauli strings**, and it always selects the configuration that minimizes this expected cost. The tensor network methods make the algorithm scalable, even for many strings and large qubit counts.  See our preprint [arXiv:2412.18973](https://arxiv.org/abs/2412.18973) for theoretical details, performance guarantees, and benchmarks against previous bounded-depth learning strategies. The Pauli string estimates are guaranteed to be at least as good as if one used $N$ shots of the equivalent-depth shallow shadows protocol, and we find that the resulting Pauli estimates only become more precise with increasing depth. 

The output of the DSS algorithm is a set of depth-`d` measurement circuits. These measurement circuits are the measurements that one should then make on the quantum computer to efficiently learn the given set of Pauli strings. The circuits are specified by specifying the 1- and 2-qubit gates. Choices of `eta`, `total_measurements`, `measurements_per_observable`, and (optionally) `weights` will affect how many and which measurement circuits are chosen. Specifying `weights` for each desired Pauli string lets you prioritize learning some Paulis over others.  And broadly speaking, a smaller `eta` corresponds to the algorithm prioritizing learning all given Paulis as many times as possible, and a larger `eta` leads the algorithm to want to learn all given Paulis at least once. 


--- 

## 📚 Citation

If you use DSS in your research, please cite:

```
@article{vankirk2024derandomized,
  title={Derandomized shallow shadows: Efficient Pauli learning with bounded-depth circuits},
  author={Van Kirk, Katherine and Kokail, Christian and Kunjummen, Jonathan and Hu, Hong-Ye and Teng, Yanting and Cain, Madelyn and Taylor, Jacob and Yelin, Susanne F and Pichler, Hannes and Lukin, Mikhail},
  journal={arXiv preprint arXiv:2412.18973},
  year={2024}
}
```

---

## 📄 License

MIT License.
