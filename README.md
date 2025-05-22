# DSS: Derandomized Single-Qubit Simulation

[![Python](https://img.shields.io/badge/python-3.8+-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/katherinevankirk/dss)](LICENSE)

**A structured simulation framework for Pauli measurements with derandomized gate configurations**  
Supported by the [Unitary Fund](https://unitary.fund)  
Relevant paper: [arXiv:2412.18973](https://arxiv.org/abs/2412.18973)

---

## 🧠 Background

This project implements methods from:

> Hu, Hong-Ye, et al. *Variance Reduction for Pauli Measurements via Derandomization*.  
> [arXiv:2412.18973](https://arxiv.org/abs/2412.18973)

It provides tools to simulate and optimize Pauli measurement circuits using structured configurations of single-qubit gates.

---

## 📦 Features

- 🧮 Define and simulate 1- and 2-qubit quantum gates
- 🔄 Apply local twirling and gate dressing to circuits
- 📉 Compute Pauli-weight-based cost functions
- 🎯 Optimize gate configurations using derandomization
- 🧰 Configure experiments via a central `DSSConfig`
- 💻 Command-line and Python API interfaces

---

## 🧰 Installation

Clone and install from [GitHub](https://github.com/katherinevankirk/dss):

```bash
git clone https://github.com/katherinevankirk/dss.git
cd dss
pip install -e .
```

---

## 🚀 Usage

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
├── config.py          # DSSConfig, file loading
├── gates.py           # Quantum gate definitions
├── circuit.py         # Dressing, single/two-qubit gate processing
├── tensor.py          # State prep, twirling
├── cost.py            # Cost and weight functions
├── derandomization.py # Optimization logic
run_dss.py             # Command-line entry point
```

---

## 📚 Citation

If you use DSS in your research, please cite:

```
@article{hu2024derandomization,
  title={Variance Reduction for Pauli Measurements via Derandomization},
  author={Hu, Hong-Ye and others},
  journal={arXiv preprint arXiv:2412.18973},
  year={2024}
}
```

---

## 📄 License

MIT License.
