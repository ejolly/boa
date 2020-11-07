from setuptools import setup, find_packages

setup(
    name="boa",
    author="Eshin Jolly",
    author_email="eshin.jolly@gmail.com",
    version="0.0.1",
    py_modules=["boa"],
    license="MIT",
    packages=find_packages(exclude=["bin"]),
    description="Environment manager for conda",
    scripts=["bin/boa_autoenv.sh"],
    install_requires=[
        "Click",
        "PyYAML"
    ],
    entry_points="""
        [console_scripts]
        boa=boa:cli
    """,
)
