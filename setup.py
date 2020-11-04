from setuptools import setup

setup(
    name="cpm",
    version="0.1",
    py_modules=["cpm"],
    scripts=["./conda_auto_env.sh"],
    install_requires=[
        "Click",
    ],
    entry_points="""
        [console_scripts]
        cpm=cpm:cli
    """,
)
