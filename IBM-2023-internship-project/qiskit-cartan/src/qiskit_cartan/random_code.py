# test an example using the transpile function
# qc_before = QuantumCircuit(3)
# qc_before.append(test_paulievolutiongate, range(3))
# print("before: ")
# print(qc_before)


# from qiskit.transpiler.passes.synthesis.high_level_synthesis import HLSConfig
# qc_after = transpile(qc_before, unitary_simulator, 
#                      hls_config=HLSConfig(paulievolutiongate=[("cartan", {})]),
#                      optimization_level=0)
# print(qc_after)


# from qiskit.transpiler.passes.synthesis.high_level_synthesis import HLSConfig, HighLevelSynthesis
# hls_pass = HighLevelSynthesis(HLSConfig(paulievolutiongate=[("cartan", {})]))
# from qiskit.converters import circuit_to_dag, dag_to_circuit
# qc_after = hls_pass.run(circuit_to_dag(qc_before))
# print("after: ")
# print(dag_to_circuit(qc_after))