from qiskit.circuit import QuantumCircuit
from qiskit.transpiler.passes.synthesis.plugin import HighLevelSynthesisPlugin
from qiskit.exceptions import QiskitError
from qiskit.circuit.library import PauliEvolutionGate

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

    # Raise an error if the object to be synthesized is not a PauliEvolutionGate
    if type(paulievolutiongate) is PauliEvolutionGate:
        raise QiskitError("Can only synthesize PauliEvolutionGate instances.")

    # Get the number of qubits of the PauliEvolutionGate
    num_qubits = paulievolutiongate.num_qubits

    # Get the Hamiltonian of the PauliEvolutionGate
    H = paulievolutiongate.operator
    
    # For now, assume that H is a Heisenberg Hamiltonian
    # Later look into involution to be used
    # But for now use a working default involution

    qc = QuantumCircuit(num_qubits)

    return qc


# define the High Level Synthesis Plugin using the above function
class CartanPlugin(HighLevelSynthesisPlugin):

    def run(self, paulievolutiongate, **options):

        print("Running Cartan Synthesis Plugin")

        return synth_cartan(paulievolutiongate)