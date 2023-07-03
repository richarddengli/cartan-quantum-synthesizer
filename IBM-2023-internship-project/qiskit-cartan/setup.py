from setuptools import setup, find_packages
# import sys
# try:
#     from skbuild import setup
# except ImportError:
#     print(
#         "Please update pip, you need pip 10 or greater,\n"
#         " or you need to install the PEP 518 requirements in pyproject.toml yourself",
#         file=sys.stderr,
#     )
#     raise


# add entrypoint for our plugin
setup(
    name="CQS-qiskit-plugin",
    version="0.1",
    packages=find_packages(),
    entry_points={
            'qiskit.synthesis': [
                'PauliEvolution.cartan = qiskit_cartan.cartan_plugin:CartanPlugin',
            ],
    },
)