from qiskit.circuit import QuantumCircuit
from qiskit.transpiler.passes.synthesis.plugin import HighLevelSynthesisPlugin
from qiskit.exceptions import QiskitError
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.quantum_info import Pauli

from CQS.methods import Hamiltonian, Cartan, FindParameters
import CQS.util.IO as IO

import numpy as np


# Define the function to synthesize a given PauliEvolutionGate
def synth_cartan(paulievolutiongate):
    """Cartan synthesis of a PauliEvolutionGate instance based on the method developed by the Kemper group.

        Args:
            paulievolutiongate (PauliEvolutionGate): a high-level definition of the unitary which implements the time evolution under a Hamiltonian consisting of Pauli terms.

        Return:
            QuantumCircuit: a circuit implementation of the PauliEvolutionGate via a Cartan Decomposition.

        Raises:
            QiskitError: if arg is not an instance of PauliEvolutionGate.
    """

    # Raise an error if the object to be synthesized is not a PauliEvolutionGate.
    if type(paulievolutiongate) is not PauliEvolutionGate:
        raise QiskitError("Can only synthesize PauliEvolutionGate instances.")

    # Get the number of qubits of the PauliEvolutionGate.
    num_qubits = paulievolutiongate.num_qubits

    # Get the time to evolve for.
    time_evolve = paulievolutiongate.time

    # Get the Hamiltonian of the PauliEvolutionGate.
    Ham = paulievolutiongate.operator

    # Get each PauliString and corresponding coefficient.
    Ham_Paulis = Ham.paulis

    Ham_PauliStrings = [pauli.to_label() for pauli in Ham_Paulis]

    # Define function to convert each string to a tuple
    # e.g "IXYZ" -> (0, 1, 2, 3).
    def pauli_string_to_tuple(pauli_string):
        pauli_mapping = {'I': 0, 'X': 1, 'Y': 2, 'Z': 3}
        pauli_tuple = tuple(pauli_mapping[pauli] for pauli in pauli_string)
        return pauli_tuple

    # Convert each string to a tuple.
    Ham_PauliTuples = list(pauli_string_to_tuple(string) for string in Ham_PauliStrings)
    Ham_PauliCoeffs = list(Ham.coeffs)
    
    # Make tuple of lists to later create Hamiltonian object.
    Ham_terms = tuple([Ham_PauliCoeffs, Ham_PauliTuples])
    
    # For now, assume that H is a Heisenberg Hamiltonian.
    # Later modify by making custom Hamiltonian.
    # Later look into involution to be used,
    # But for now use a working default involution.

    # Make empty CQS Hamiltonian object.
    CQS_Ham = Hamiltonian(num_qubits)

    # Add each term to CQS Hamiltonian.
    CQS_Ham.addTerms(Ham_terms)

    # Check each term has been added.
    print(CQS_Ham.getHamiltonian(type="printText"))

    # Try to perform a Cartan involution on the Hamiltonian
    # using the defauls evenOdd Decomposition.
    # If H is not contained in the -1 eigenspace, raise an error.
    try:
        CQS_Cartan = Cartan(CQS_Ham)
    except Exception as e:
        print(e)

    # Generate the parameters via classical optimization of the cost function.
    CQS_parameters = FindParameters(CQS_Cartan)

    # Store results.
    kTuples = CQS_parameters.cartan.k
    kCoefs = CQS_parameters.kCoefs
    hTuples = CQS_parameters.cartan.h
    hCoefs = CQS_parameters.hCoefs

    # Make Qiskit Quantum Circuit.
    qc = QuantumCircuit(num_qubits)
    qc.barrier()

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


# Testing.
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.opflow import I, X, Y, Z
test_heisenberg_ham = (X^X^I) + (Y^Y^I) + (Z^Z^I) + (I^X^X) + (I^Y^Y) + (I^Z^Z)
test_time_evolve = 3
test_paulievolutiongate = PauliEvolutionGate(test_heisenberg_ham, time=test_time_evolve)
qc = synth_cartan(test_paulievolutiongate)
print(qc)

from qiskit import Aer, transpile
unitary_simulator = Aer.get_backend('unitary_simulator')
qc_transp = transpile(qc, unitary_simulator)
final_unitary_cartan = unitary_simulator.run(qc_transp).result().get_unitary()

import scipy
from qiskit.quantum_info import SparsePauliOp
H = SparsePauliOp(["XXI", "YYI", "ZZI", "IXX", "IYY", "IZZ"], 
                  np.array([1, 1, 1, 1, 1, 1])).to_matrix()
propagator = scipy.linalg.expm(-1j*H*test_time_evolve)
matrix_norm = np.linalg.norm(propagator - final_unitary_cartan)
print("matrix norm of the difference between the ideal propagator and that obtained by cartan decomposition: \n",
       matrix_norm)


# Define the High Level Synthesis Plugin.
class CartanPlugin(HighLevelSynthesisPlugin):

    def run(self, paulievolutiongate, **options):

        print("Running Cartan Synthesis Plugin")

        return synth_cartan(paulievolutiongate)