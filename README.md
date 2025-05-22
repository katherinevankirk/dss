# DSS: Derandomized Shallow Shadows

[![Python](https://img.shields.io/badge/python-3.8+-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/katherinevankirk/dss)](LICENSE)

**A structured framework for efficiently estimating Pauli string observables with bounded-depth measurements**  
Supported by the [Unitary Fund](https://unitary.fund)  

---

## 🧠 Background

This project implements methods from:

> Katherine Van Kirk, Christian Kokail, Jonathan Kunjummen, Hong-Ye Hu, Yanting Teng, Madelyn Cain, Jacob Taylor, Susanne F. Yelin, Hannes Pichler, and Mikhail Lukin. *Derandomized shallow shadows: Efficient Pauli learning with bounded-depth circuits*.  
> [arXiv:2412.18973](https://arxiv.org/abs/2412.18973)

It provides tools to run the derandomized shallow shadows (DSS) algorithm, which optimizes shallow measurement circuits for learning a given set of Pauli strings. The algorithm specifies some set of $N$ measurement circuits, which rotate into the desired measurement bases. Crucially, these $N$ measurement circuits each contain at most depth $d$ layers of two qubit gates, and the algorithm determines these circuits by derandomizing shallow shadows. Exploiting tensor network techniques that mimic classical Markovian processes, our algorithm optimizes shallow circuits to maximize the probability of learning the given set of Pauli strings. We find effective, shallow circuits by selecting circuits with high probability of learning the Pauli strings.  

---

## 📦 Features

- 🧮 Homemade, special-purpose tensor network contraction functions
- 📉 Compute cost functions based on probability of learning a set of Pauli strings
- 🎯 Optimize short-depth measurement circuits using derandomization
- 🧰 Configure derandomization procedure via a central `DSSConfig`
- 💻 Command-line and Python API interfaces

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

We provide several avenues for implementing the DSS algorithm. Moreover, we also include two Pauli string text files (pauli_strings_30 and pauli_strings_bell), which one can use to run examples. The first example, `pauli_strings_30.txt` contrains 30 different length-8 Pauli strings, and the second example `pauli_strings_bell.txt` contrains 3 Pauli strings, which commute and are simultaneously diagonalized by the bell basis. Either example may be tested by specifying the length $N$ of the strings, the `depth` of the measurement circuit, the hyperparameter `eta`, and the total number of desired measurements `total_measurements`.

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
    filepath="pauli_strings_bell.txt",
    N=8,
    depth=3,
    eta=0.9,
    total_measurements=100,
    measurements_per_observable=100
)
results = full_derandomization(config)
```

---

## 📄 Input Format

### Pauli Strings

Each line in your `.txt` file should be a valid Pauli string:

```
IXIXYXYY
XIYIIIZZ
XYXZXIXX
...
```

You may also use `pauli_strings_bell.txt` for simpler examples.

### Optional: Weights

If used, weights can be loaded from a `weights.txt` file with one float per line.

---

## 🧱 Project Structure

```
dss/
├── config.py                  # DSSConfig, file loading
├── gates.py                   # Quantum gate definitions
├── circuit.py                 # Dressing, single/two-qubit gate processing
├── tensor_constractions.py    # State prep, twirling
├── cost.py                    # Cost and weight functions
├── derandomization.py         # Optimization logic
run_dss.py                     # Command-line entry point
```

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
