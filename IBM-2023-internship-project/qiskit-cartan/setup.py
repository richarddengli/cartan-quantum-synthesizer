import sys


try:
    from skbuild import setup
except ImportError:
    print(
        "Please update pip, you need pip 10 or greater,\n"
        " or you need to install the PEP 518 requirements in pyproject.toml yourself",
        file=sys.stderr,
    )
    raise


# add entrypoint for our plugin
setup(
    entry_points={
            'qiskit.transpiler.init': [
                'cartan = qiskit_cartan.cartan_plugin:CartanPlugin',
            ],
    },
)