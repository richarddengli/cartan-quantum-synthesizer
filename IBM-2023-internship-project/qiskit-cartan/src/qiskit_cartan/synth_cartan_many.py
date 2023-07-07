from qiskit.circuit import QuantumCircuit
from qiskit.exceptions import QiskitError
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.quantum_info import Pauli

from CQS.methods import Hamiltonian, Cartan, FindParameters
import CQS.util.IO as IO

import numpy as np
import random
import itertools

# Define the function to create a Qiskit QuantumCircuit given Cartan parameters.
def generate_cartan_circuit(CQS_Cartan, time_evolve):
    
    # Generate the parameters via classical optimization of the cost function.
    CQS_parameters = FindParameters(CQS_Cartan)

    # Store results.
    kTuples = CQS_parameters.cartan.k
    kCoefs = CQS_parameters.kCoefs
    hTuples = CQS_parameters.cartan.h
    hCoefs = CQS_parameters.hCoefs

    num_qubits = CQS_Cartan.hamiltonian.sites

    # Make Qiskit Quantum Circuit.
    qc = QuantumCircuit(num_qubits)

    # K^\dag.
    for kTuple, kCoef in zip(kTuples, kCoefs):

        kString = str(IO.paulilabel(kTuple))
        gate = PauliEvolutionGate(Pauli(kString[::-1]), time=kCoef) 
        qc.append(gate, range(num_qubits))

    qc.barrier()

    # H.
    for hTuple, hCoef in zip(hTuples, hCoefs):

        hString = str(IO.paulilabel(hTuple))
        gate = PauliEvolutionGate(Pauli(hString[::-1]), 
                                time=np.real(hCoef)*time_evolve) # WLOG convert complex to real
        qc.append(gate, range(num_qubits))

    qc.barrier()

    # K.
    for kTuple, kCoef in reversed(list(zip(kTuples, kCoefs))):

        kString = str(IO.paulilabel(kTuple))
        gate = PauliEvolutionGate(Pauli(kString[::-1]), time=-kCoef)
        qc.append(gate, range(num_qubits))

    return qc


# Define function to convert each string to a tuple
# e.g "IXYZ" -> (0, 1, 2, 3).
def pauli_string_to_tuple(pauli_string):

    pauli_mapping = {'I': 0, 'X': 1, 'Y': 2, 'Z': 3}
    pauli_tuple = tuple(pauli_mapping[pauli] for pauli in pauli_string)
    
    return pauli_tuple


# Define the function to synthesize a given PauliEvolutionGate many 
# different times, or once if lexicographic.
def synth_cartan_many(paulievolutiongate, 
                          random_seed,
                          size,
                          lexicographic):
    """Cartan synthesis of a PauliEvolutionGate instance based on the method developed by the Kemper group.

        Args:
            paulievolutiongate (PauliEvolutionGate): a high-level definition of the unitary which implements
            the time evolution under a Hamiltonian consisting of Pauli terms.
            random_seed: seed used to set the ordering of factors in K and the starting element of h.
            size: number of circuits to generate.
            lexicographic: whether or not pauli factors in K are lexicographically ordered.

        Return:
            List: a list of QuantumCircuits implementing the PauliEvolutionGate via a Cartan Decomposition.

        Raises:
            QiskitError: if arg is not an instance of PauliEvolutionGate.
    """

    # Raise an error if the object to be synthesized is not a PauliEvolution.
    if type(paulievolutiongate) is not PauliEvolutionGate:

        raise QiskitError("Can only synthesize PauliEvolution instances.")

    # Get the number of qubits of the PauliEvolution.
    num_qubits = paulievolutiongate.num_qubits

    # Get the time to evolve for.
    time_evolve = paulievolutiongate.time

    # Get the Hamiltonian of the PauliEvolution.
    Ham = paulievolutiongate.operator

    # Get each PauliString and corresponding coefficient.
    Ham_Paulis = Ham.paulis

    Ham_PauliStrings = [pauli.to_label() for pauli in Ham_Paulis]

    # Convert each string to a tuple.
    Ham_PauliTuples = list(pauli_string_to_tuple(string) for string in Ham_PauliStrings)
    Ham_PauliCoeffs = list(Ham.coeffs)
    
    # Make tuple of lists to later create Hamiltonian object.
    Ham_terms = tuple([Ham_PauliCoeffs, Ham_PauliTuples])
    
    # Later look into involution to be used,
    # But for now use a working default involution.

    # Make empty CQS Hamiltonian object.
    CQS_Ham = Hamiltonian(num_qubits)

    # Add each term to CQS Hamiltonian.
    CQS_Ham.addTerms(Ham_terms)

    # Check each term has been added.
    # print(CQS_Ham.getHamiltonian(type="printText"))

    # Try to perform a Cartan involution on the Hamiltonian
    # using the defauls evenOdd Decomposition.
    # If H is not contained in the -1 eigenspace, raise an error.
    try:

        CQS_Cartan = Cartan(CQS_Ham, manualMode=1)
        CQS_Cartan.g = CQS_Cartan.makeGroup(CQS_Cartan.HTuples)
        CQS_Cartan.decompose(involutionName = 'evenOdd')

    except Exception as e:

        print(e)

    # Set the chosen random seed.
    # Randomly choose an element of m as a starting element
    # of the Cartan subalgebra h.
    # Then generate all possible permutations of k.
    # If lexicographic == True, check size is 1 (lexicographic ordering is unique)
    # and then sort k in place. Then generate circuit for k.
    # Otherwise sample from all perms and generate circuit for each.
    random.seed(random_seed)
    
    if lexicographic:

        assert size == 1
        CQS_Cartan.k.sort() 
        CQS_Cartan.subAlgebra(seedList = [random.choice(CQS_Cartan.m)]) 
        qc = generate_cartan_circuit(CQS_Cartan, time_evolve)

        return [qc]
    
    else:

        k_perms = list(itertools.permutations(CQS_Cartan.k))
        sampled_k_perms = random.sample(k_perms, size)
        qc_list = []

        for sampled_k_perm in sampled_k_perms:

            CQS_Cartan.k = list(sampled_k_perm)
            CQS_Cartan.subAlgebra(seedList = [random.choice(CQS_Cartan.m)])
            qc = generate_cartan_circuit(CQS_Cartan, time_evolve)
            qc_list.append(qc)

        return qc_list
