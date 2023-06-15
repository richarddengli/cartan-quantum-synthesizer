# IBM 2023 internship project - Qiskit Transpiler Plugin for Fixed-Depth Hamiltonian Simulation using Cartan Decomposition

## Authors
Richard Li, Nick Bronn, Olivia Lanes (IBM Quantum Community Team)

## Summary
This is the folder for my summer 2023 internship at IBM supervised by Dr. Nick Bronn and Dr. Olivia Lanes. The first goal of the project is to write a Qiskit plugin for the technique developed in [Fixed Depth Hamiltonian Simulation via Cartan Decomposition](https://arxiv.org/pdf/2104.00728.pdf) and implemented as the code contained in the parent folder. In particular, we will make use of an entry point in the `init` stage of the `PassManager` to incorporate the implemented code as an `UnitarySynthesis` pass. Such a plugin will allow us to generate efficient circuits for simulating the time evolution of several types of lattice models constrained by the native gate set, connectivity, and the heavy-hex layout of IBM-Q processors. Then by generating a large number of different circuits by changing the choice of the classical optimizer and the type of involution, we hope to train a neural network that quickly and optimally transpiles the theoretical unitary circuit corresponding to the time-evolution of the desired Hamiltonian into the actual unitary circuit executed on the real hardware. If successful, this will allow IBM-Q users to perform quantum simulation tasks with fewer resources and at a higher accuracy.

## Folder structure
- `qiskit-toqm` is an example repo containing qiskit transpiler passes and plugins for the Time-Optimal Qubit Mapping (TOQM) algorithm.
- `qiskit-cartan` is our repo which implements the desired cartan decomposition plugin. Its structure is inspired by that of `qiskit-toqm`.

## References
- Links:
  - [Qiskit API documentation on the transpiler](https://qiskit.org/documentation/apidoc/transpiler.html). A detailed explanation of the transpiler in Qiskit.
  - [Qiskit tutorial on the transpiler](https://qiskit.org/documentation/tutorials/circuits_advanced/04_transpiler_passes_and_passmanager.html). An detailed tutorial on the transpiler in Qiskit.
  - [Qiskit API documentation on transpiler plugins](https://qiskit.org/documentation/apidoc/transpiler_plugins.html). An detailed explanation of transpiler plugins in Qiskit.
  - [Summary of Cartan decomposition technique](https://thomassteckmann.com/quantum.html). A concise overview of the Cartan decomposition technique for Hamiltonian simulation provided by one of its principal authors, Thomas Steckmann.
  - [IBM research blog on the heavy-hex lattice](https://research.ibm.com/blog/heavy-hex-lattice). An overview of the motivation and properties of the heavy-hex qubit connectivity employed by many current and all future IBM-Q devices.
  - [Entry points guide by Setuptools](https://setuptools.pypa.io/en/latest/userguide/entry_point.html). User guide on Entry Points which Qiskit plugins use.
- Papers:
  - [Quantum Simulation on Noisy Superconducting Quantum Computers](https://arxiv.org/pdf/2209.02795.pdf). A detailed introduction to simulating quantum systems on NISQ-hardware.


## Notes on set up on my machine
conda environment installed from source (stable):
- name: `qiskit_stable_env`
- instructions to install: 
```
git clone https://github.com/qiskit-community/qiskit-research.git
cd qiskit-research
(if needed) set SETUPTOOLS_ENABLE_FEATURES=legacy-editable
pip install -e .
```
This env also contains installations of the `cartan-quantum-synthesizer` and `qiskit-toqm`. Additionally, one may need to run `pip install scikit-build`.

conda environment installed from source (dev):
- name: `qiskit_dev_env`
- instructions to install: 
```
git clone https://github.com/qiskit/qiskit-terra
cd qiskit-terra
(if needed) set SETUPTOOLS_ENABLE_FEATURES=legacy-editable
pip install -e .
```

I anticipate most of the work to be done in the stable environment initially given that transpiler plug-ins are "consumed" by Qiskit and do not inherently change it. However, we may sometimes use the dev environment in order to directly change certain parameters and alter parts of the workflow. 