import math
import numpy as np


from dss.cost import calculate_weight_structure, confidence_cost_function_structure, confidence_cost_function_single_qubit, weight_of_all_Paulis
from dss.config import DSSConfig




# --------------------------------- DSS DATABASE CONFIGURATION TO SPEED UP DERANDOMIZATION ------------------------------------- #



def setup_structure_database(N, depth, pauli_masks):
    """
    Precompute and store weight vectors for each Pauli mask under a fixed random single-qubit configuration.

    This function generates a default single-qubit gate configuration (all gates set to index 3),
    then computes the associated weight vector for each Pauli string mask using `calculate_weight`.
    The result is stored in a dictionary, keyed by the serialized configuration.

    Args:
        N (int): Number of qubits.
        depth (int): Circuit depth (number of layers).
        pauli_masks (np.ndarray): Boolean array of shape (num_strings, N), where True indicates a non-identity Pauli operator.

    Returns:
        dict[bytes, list[float]]: A dictionary mapping configuration keys (as bytes) to lists of computed weights.
    """

    structure_database = {}
    random_gates = 3* np.ones((depth,N//2))

    weight_list_to_save = []
    for l in range(len(pauli_masks)):
        weight_pauli_l = calculate_weight_structure(N, pauli_masks[l], depth, random_gates)
        weight_list_to_save.append(weight_pauli_l)

    structure_database[random_gates.tobytes()] = weight_list_to_save

    return structure_database




# ------------------------------------------- DSS DERANDOMIZATION FUNCTIONS ---------------------------------------------------- #




# === Derandomization Routines ===


def structure_derandomization(dss_data: DSSConfig, m, count_hits, single_qubit_database, structure_database, verbose = False):
    """
    Implementation of the TWO QUBIT STRUCTURE DERANDOMIZATION
    (0=>identity, 1=>CNOT, 2=>swap)
    
    Args:
        m (Int): the current measurement number we are derandomizing
        count_hits (list of Ints): number of times each Pauli has been measured by previous measurements
        num_of_measurements_per_observable (Int): int for the number of measurements per observable
        weight (list of Floats): None or a list of coefficients for each observable
                 None -- neglect this parameter
                 a list -- modify the number of measurements for each observable by the corresponding weight
    
    Returns:
        best_config (2D-array of Ints): the 2D array specifies all twoqubit gates in a single measurement
            --> each row represents a different layer (starting from the measurements then moving backward)
            --> brickwork pattern: first layer starts with gates on 0<>1, 2<>3, 4<>5, etc. next starts with 1<>2, 3<>4, etc... 
            --> key: 0=>identity, 1=>CNOT, 2=>swap
    """
   
    if verbose:
        print('\nSTRUCTURE DERANDOMIZATION')
    
    best_config = 3* np.ones((dss_data.depth,dss_data.N//2))
    best_config = best_config.astype(int)
    best_cost = 100000

    
    for l in range(dss_data.depth):
        for g in range(dss_data.N//2):
            best_config[l][g] = 0
            for gate in range(3): 
                this_config = np.array(best_config)
                this_config[l][g] = gate
                this_cost = confidence_cost_function_structure(dss_data.N, dss_data.depth, dss_data.eta, dss_data.max_num_measurements, m, this_config, dss_data.pauli_masks, count_hits, structure_database, dss_data.weights, dss_data.measurements_per_observable)

                if verbose: 
                    print(m, ':', this_config, '->', this_cost)

                if this_cost < best_cost: 
                    best_config = this_config
                    best_cost = this_cost
    
    if verbose: 
        print('two-qubit gates chosen:', best_config, '\n')

    return best_config 




def single_qubit_derandomization(dss_data, m, best_two_qubit_gates, count_hits, single_qubit_database, structure_database, verbose = False):
    """
    Implementation of the SINGLE QUBIT DERANDOMIZATION
    
    Args:
        m (Int): the current measurement number we are derandomizing
        best_two_qubit_gates (2D array): the chosen structure (ie. two qubit gates) for this measurement
        count_hits (list of Ints): number of times each Pauli has been measured by previous measurementsnum_of_measurements_per_observable (Int): int for the number of measurements per observable
        num_of_measurements_per_observable (Int): int for the number of measurements per observable
        weight (list of Floats): None or a list of coefficients for each observable
                 None -- neglect this parameter
                 a list -- modify the number of measurements for each observable by the corresponding weight
    
    Returns:
        best_single_qubit_gates (1D array of Ints): specifies the 1qubit gates in a single measurement, starting from the last layer
        --> options: 1,2,3,4,5,6 (as defined above)
        --> convention: 1st gate in array is at the top of the last layer (last = closest to measurement); 
                        second gate is one qubit down;  this continues in snake pattern.
    """

    if verbose: 
        print('SINGLE QUBIT DERANDOMIZATION')
    
    best_single_qubit_gates = np.zeros(dss_data.N*(dss_data.depth+1))
    best_single_qubit_gates = best_single_qubit_gates.astype(int)
    min_cost = 1000
    
    for single_qubit_box in range(dss_data.N*(dss_data.depth+1)):
        
        #always at least replace random with identity
        best_single_qubit_gates[single_qubit_box] = 1
        
        for gate_choice in range(1,7):
            test_one_gates = np.copy(best_single_qubit_gates)
            test_one_gates[single_qubit_box] = gate_choice
            
            cost_test = confidence_cost_function_single_qubit(dss_data.N, dss_data.depth, dss_data.eta, dss_data.max_num_measurements, m, test_one_gates, best_two_qubit_gates, dss_data.pauli_strings_to_learn, dss_data.pauli_masks, count_hits, structure_database, single_qubit_database, dss_data.weights, dss_data.measurements_per_observable)
            
            if cost_test < min_cost:
                min_cost = cost_test
                best_single_qubit_gates = test_one_gates
    
    if verbose: 
        print('single-qubit gates chosen:', best_single_qubit_gates, '\n\n')

    return best_single_qubit_gates




# measurements_per_observable, N, depth, eta,max_num_measurements,pauli_strings_to_learn,pauli_masks
# def full_derandomization(num_of_measurements_per_observable, system_size, depth, eta, max_num_measurements, pauli_strings_to_learn, pauli_masks, single_qubit_database, structure_database, weight = None, verbose = False):


def full_derandomization(dss_data: DSSConfig, verbose = False):
    """
    Implementation of derandomized shallow shadows
    
    Args:
        num_of_measurements_per_observable (Int): int for the number of measurements per observable
        system_size (Int): int for how many qubits in the quantum system
        weight (list of Floats): None or a list of coefficients for each observable
                 None -- neglect this parameter
                 a list -- modify the number of measurements for each observable by the corresponding weight
    
    Returns:
        structure_measurement_settings (list of 2D-array of Ints): each 2D array specifies all twoqubit gates in a single measurement
        measurement_settings (list of 1D array of Ints): each 1D array specifies the 1qubit gates in a single measurement
        count_hits (list of Ints): list of how many times ea Pauli string was measured by given measurement settings
    """

    single_qubit_database = {}
    structure_database = setup_structure_database(dss_data.N, dss_data.depth, dss_data.pauli_masks)

    structure_measurement_settings = []
    measurement_settings = []
    count_hits = np.zeros(len(dss_data.pauli_masks))  # how many times ea observable has been measured so far

    for m in range( dss_data.measurements_per_observable * len(dss_data.pauli_masks) ):
        
        # TWO QUBIT STRUCTURE DERANDOMIZATION (0=>identity, 1=>CNOT, 2=>swap)
        best_two_qubit_gates = structure_derandomization(dss_data, m, count_hits, single_qubit_database, structure_database, verbose) 
        structure_measurement_settings.append(best_two_qubit_gates)
        
        # SINGLE QUBIT DERANDOMIZATION
        best_single_qubit_gates = single_qubit_derandomization(dss_data, m, best_two_qubit_gates, count_hits, single_qubit_database, structure_database, verbose)
        measurement_settings.append(best_single_qubit_gates)

        # UPDATE COUNT HITS
        count_hits = count_hits + weight_of_all_Paulis(dss_data.N, best_single_qubit_gates, best_two_qubit_gates, dss_data.pauli_strings_to_learn)
        print('derandomizing measurement', m)
        print('-------------------------------')
        print('number of times each Pauli has been measured so far:\n', count_hits,'\n')


        # END DERANDOMIZATION if either condition below is satisfied: 
        ### Condition #1 -- you reached your measurement budget
        if m == dss_data.max_num_measurements:
            return structure_measurement_settings, measurement_settings, count_hits
        ### Condition #2 -- you measured each Pauli the desired number of times
        success = 0
        for i in range(len(dss_data.pauli_masks)):
            if count_hits[i] >= math.floor(dss_data.weights[i] * dss_data.measurements_per_observable):
                success += 1
        if success == len(dss_data.pauli_masks):
            return structure_measurement_settings, measurement_settings, count_hits
        

    return structure_measurement_settings, measurement_settings, count_hits




