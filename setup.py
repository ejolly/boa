from setuptools import setup

setup(
    name="boa",
    version="0.1",
    py_modules=["boa"],
    scripts=["./conda_auto_env.sh"],
    install_requires=[
        "Click",
        "PyYAML"
    ],
    entry_points="""
        [console_scripts]
        boa=boa:cli
    """,
)
