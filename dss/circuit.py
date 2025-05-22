
import numpy as np

from dss.gates import identity_gate, swap_gate, cnot_gate, u2_gate
from dss.gates import random_singleq_gate




# ---------------------------- HELPER FUNCTIONS FOR BUILDING UP CIRCUITS -------------------------- #




# === Defining Measurement (Z) Basis ===

def initial_state(mask, N):
    return np.where(mask[:, None], np.array([0, 0, 0, 1.]), np.array([1., 0, 0, 0]))

def initial_state_sig(mask, N):
    return np.where(mask[:, None], np.array([0, 1.]), np.array([1., 0]))




# === Twirling Operations ===

def local_twirl(two_q_gate):
    tw = random_singleq_gate()
    return np.einsum('ia,jb,ck,dl,abcd->ijkl',tw,tw,tw,tw,two_q_gate)

def local_twirl_sig(two_q_gate):
    twrld_gate = local_twirl(two_q_gate)
    part2 = np.concatenate((twrld_gate[:,:,0:1,:], np.sum(twrld_gate[:,:,1:,:],axis=2,keepdims = True)),axis = 2)
    part3 = np.concatenate((part2[:,:,:,0:1], np.sum(part2[:,:,:,1:],axis=3,keepdims = True)),axis = 3)
    return part3[0:2,0:2,:,:]

def make_twrld_sig_twoq_set():
    #These are the original two qubit gates, with local twirling already carried out on all four indices:
    tw_id, tw_cx, tw_sw, tw_u2 = [local_twirl(g) for g in [identity_gate(),cnot_gate(),swap_gate(),u2_gate()]]
    return [local_twirl_sig(g) for g in [tw_id,tw_cx,tw_sw,tw_u2]]
