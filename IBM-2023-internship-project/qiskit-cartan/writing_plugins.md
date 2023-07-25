# How to write and use a Qiskit transpiler plugin
In this file, we will outline all the steps necessary to write and use a custom Qiskit transpiler plugin. This is meant to supplement the existing Qiskit tutorials and documentation.

# Introduction
Transpilation is the process of transforming some abstract or high-level quantum circuit into an equivalent or nearly equivalent circuit executable on the desired backend. In Qiskit, this overall transformation is composed of individual circuit transformations known as "transpiler passes". Often these passes are grouped together into "stages" according to the nature of the transformation they affect. A `PassManager` object organizes how its stages (if it has any) and their respective passes are ordered and scheduled. For example, the `transpile()` function by default generates a preset staged PassManager. 

While Qiskit offers a variety of built-in passes, the transpilation workflow can be customized freely by the user by writing their own passes (for example, see section "Implementing a BasicMapper Pass" of [this tutorial](https://qiskit.org/documentation/tutorials/circuits_advanced/04_transpiler_passes_and_passmanager.html#Implementing-a-BasicMapper-Pass)). Transpiler "plugins" build on top of this, allowing users to interface custom passes directly with `transpile()` and different PassManagers. Currently there are two categories of plugins available: (1) [preset passmanager plugins](https://qiskit.org/documentation/apidoc/transpiler_plugins.html) and (2) [synthesis plugins](https://qiskit.org/documentation/apidoc/transpiler_synthesis_plugins.html#module-qiskit.transpiler.passes.synthesis.plugin). Plugins function by using the more general functionality of [entry points](https://setuptools.pypa.io/en/latest/userguide/entry_point.html) in the `setuptools` Python library.

## Writing a plugin
To write a plugin, follow these steps.

1. Activate a Python virtual environment and install Qiskit. 
2. Create a master directory for the plugin called `<master_repo_name>` with the subfolder called `src\<source_subfolder_name>`. This subfolder will contain the source code for the plugin (separating it from other auxilliary files, such as documentation, testing, and the like). The "src" is not strictly necessary, but it is a good reminder of its purpose.
3. In `src\<source_folder_name>`, create an empty `__init__.py` file. This will tell Python to treat the `src\<source_folder_name>` folder as a Python package (to be later interfaced with Qiskit).
4. In `src\<source_folder_name>`, create an empty `<plugin_file_name>.py` file. 
5. In `<plugin_file_name>.py`, we shall inherit a Qiskit plugin class. Here we demonstrate with the example of inheriting a `HighLevelSynthesisPlugin` class, thereby creating a plugin for a high-level synthesis pass. This pass traverses each gate of a `QuantumCircuit` instance; if that gate is a highlevel_object, we shall synthesize it using a custom function `convert_highlevel_object`. This is implemented by the following code:


    
    ```
    def convert_highlevel_object(highlevel_object, **options):
        ...
        return ...


    class <plugin_sublass_name>(HighLevelSynthesisPlugin):

        def run(self, highlevel_object, **options):
            ...
            return convert_highlevel_object(highlevel_object, **options)
    ```

6. For the same example above, in `<master_repo_name>`, create a `setup.py` file and write the following to inferface the plugin with Qiskit.

    ```
    from setuptools import setup, find_packages

    setup(
    entry_points={
            'qiskit.synthesis': [
                'highlevel_object_name.<plugin_name> = <source_folder_name>.<plugin_file_name>:<plugin_subclass_name>',
            ],
    },
    )

    ```
`plugin_name` can be chosen freely. For your own plugin, replace `qiskit.synthesis` with the appropriate `<plugin_group_name>`. Also replace `highlevel_object_name` with the `name` attribute of the type of object to be synthesized (which can be found by running `object.name`).


## Using a plugin
To use a plugin, follow these steps.

1. On the command line, `cd` into `<master_repo_name>`.
2. On the command line, install the plugin by running `pip install -e .`.
3. Check that the plugin is correctly installed. For the example above, run the following code:
    ```
    from qiskit.transpiler.passes.synthesis.plugin import HighLevelSynthesisPluginManager
    HLS_plugin_manager = HighLevelSynthesisPluginManager()
    print(HLS_plugin_manager.plugins.names())
    ```
4. Run the following:
    ```
    from qiskit.transpiler.passes.synthesis.high_level_synthesis import HLSConfig

    hls_config = HLSConfig(<highlevel_object_name>=[("<plugin_name>", {**options})])
    ```
    Ajust the code accordingly for your own plugin.

    Then to use the high-level plugin as a single transpiler pass, run the following:
    ```
    from qiskit.transpiler import PassManager
    
    pm = PassManager()
    pm.append(HighLevelSynthesis(hls_config=hls_config))
    qc_after = pm.run(qc_before)
    ```
    where `qc_before` is the circuit to be transpiled.

    Alternatively, to use the plugin as part of a complete transpilation workflow as , run the following:
    ```
    from qiskit.compiler import transpile

    qc_after = transpile(qc_before, backend, hls_config=hls_config)
    ```
    where `backend` is the target backend.



## Tips
- To debug any transpilation issues, it is helpful to run
    ```
    import logging

    logging.basicConfig(level='DEBUG')
    ```
    before any testing. To stop logging, just run
    ```
    logging.basicConfig()
    ```