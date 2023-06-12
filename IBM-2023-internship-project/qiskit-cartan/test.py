from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit.providers.fake_provider import FakeTokyo

# Get the passes from the init stage of a preset PassManager instance,
# which is the default pass managers used by the transpile() function.
backend = FakeTokyo()

pm = generate_preset_pass_manager(0, backend=backend) #backend = backend is optional
print("\n")
print(pm.init.passes())

# When the backend is not specified, pm.init.passes only contains only an analysis pass
# to detect if the DAG contains a specific instruction. Otherwise, it also contains \
# unitary synthesis, high level synthesis, and unroll_3q_or_more.