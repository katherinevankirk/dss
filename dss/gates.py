
import numpy as np


# --------------------------------- DEFINING 1 AND 2 QUBIT GATES AS TENSORS ------------------------------------- #


# === Two-Qubit Gate Definitions ===
def identity_gate() -> np.ndarray:
    """Return the 4D identity tensor gate (shape: 4x4x4x4)."""
    return np.eye(16).reshape(4, 4, 4, 4)

def swap_gate() -> np.ndarray:
    """Return the 4D SWAP tensor gate (shape: 4x4x4x4) by transposing slices of the identity gate."""
    swapgate = identity_gate()
    return np.array([[gate.transpose() for gate in row] for row in identity_gate()])

def cnot_gate():
    """Return the 4D CNOT tensor gate (shape: 4x4x4x4) by first defining CNOT on Pauli basis 
      ---> BASIS ORDERING : For the two-qubit Pauli operators, we define the two-qubit basis
           states in the following order... ['II',  'IX',  'IY',  'IZ',  'XI',  'XX',  'XY',  
           'XZ',  'YI',  'YX',  'YY',  'YZ',  'ZI',  'ZX',  'ZY',  'ZZ'] 
    """
    CNOT_MPO = np.array([  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                           [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                           [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])

    return CNOT_MPO.reshape(4,4,4,4)

def u2_gate() -> np.ndarray:
    """Return a custom U2 tensor gate with dominant identity at (0,0) and scaled elsewhere."""
    first_site = identity_gate()[0][0]
    all_other_sites = (2/30) * (np.ones((4,4)) - first_site)

    the_u2 = []
    for r in range(4):
        this_gate = []
        for c in range(4):
            if r == 0 and c == 0:
                this_gate.append(first_site)
            else:
                this_gate.append(all_other_sites)
        the_u2.append(this_gate)

    return np.array(the_u2)



# === Single-Qubit Gate Definitions ===

def gate1(): 
    return np.array([[1.,0,0,0],[0,1.,0,0],[0,0,1.,0],[0,0,0,1.]])

def gate2(): 
    return np.array([[1.,0,0,0],[0,1.,0,0],[0,0,0,1.],[0,0,1.,0]])

def gate3(): 
    return np.array([[1.,0,0,0],[0,0,1.,0],[0,1.,0,0],[0,0,0,1.]])

def gate4(): 
    return np.array([[1.,0,0,0],[0,0,0,1.],[0,1.,0,0],[0,0,1.,0]])

def gate5(): 
    return np.array([[1.,0,0,0],[0,0,1.,0],[0,0,0,1.],[0,1.,0,0]])

def gate6(): 
    return np.array([[1.,0,0,0],[0,0,0,1.],[0,0,1.,0],[0,1.,0,0]]) #HADAMARD

def random_singleq_gate():
    singleq_random_MPO = np.array([[1,0,0,0],
                               [0,1.0/3.0,1.0/3.0,1.0/3.0],
                               [0,1.0/3.0,1.0/3.0,1.0/3.0],
                               [0,1.0/3.0,1.0/3.0,1.0/3.0]])
    return singleq_random_MPO




