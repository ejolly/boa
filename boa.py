#!/Users/Esh/anaconda3/bin/python
"""
Main CLI run time
"""

from pathlib import Path
import click
from subprocess import call
import yaml
import shutil

# import subprocess
# import os


def split_conda_pip(deps):
    currentpip = [e for e in deps if isinstance(e, dict) and "pip" in e.keys()]
    if len(currentpip):
        currentpip = currentpip[0]
        currentpip = currentpip["pip"]
    everythingelse = [
        e
        for e in deps
        if isinstance(e, str) or (isinstance(e, dict) and "pip" not in e.keys())
    ]
    return currentpip, everythingelse


@click.group()
def cli():
    """
    Boa is a wrapper around conda to make environment management easier. Call it with the sub-commands below
    """
    pass


@cli.command()
@click.argument(
    "pyv",
    required=False,
)
def init(pyv):
    """
    Initialize an environment.yml file with an optionally specified Python version and Boa. Python version should be specified as a string, e.g. 'python-3.6'. Default: 3.8.
    """

    if pyv is None:
        pyv = "python=3.6"
    env_file = Path("./environment.yml")
    if not env_file.exists():
        envdict = {
            "name": "null",
            "dependencies": [
                f"{pyv}",
                "pip",
                {"pip": ["git+https://github.com/ejolly/boa"]},
            ],
        }
        with open("environment.yml", "w") as f:
            _ = yaml.dump(envdict, f, sort_keys=True)
        click.echo("created environment.yml")
        click.echo("use 'boa install' to build environment (install conda packages)")


@cli.command()
def clean():
    """
    Compeletely remove installed environment packages
    """
    try:
        shutil.rmtree("./env")
        click.echo("removed all installed packeges")
        click.echo("use 'boa install' to rebuild environment")
    except FileNotFoundError as _:  # noqa
        click.echo("no installed packages found")


@cli.command()
def list():
    """
    Show package version from environment.yml
    """
    env_file = Path("./environment.yml")
    if env_file.exists():
        click.echo("Environment Packages:")
        with open(str(env_file), "r") as f:
            envdict = yaml.load(f, Loader=yaml.FullLoader)
            deps = envdict["dependencies"]
            for dep in deps:
                if isinstance(dep, str):
                    click.echo(dep)
                elif isinstance(dep, dict) and "pip" in dep.keys():
                    click.echo("pip-dependencies:")
                    for ddep in dep.values():
                        for d in ddep:
                            click.echo(f"  {d}")
    else:
        raise FileNotFoundError("No environment.yml found. Did you run 'boa init'?")


@cli.command()
@click.argument("libraries", nargs=-1, required=False)
@click.option(
    "--pip",
    is_flag=True,
    default=False,
    help="Assume install should happen with pip instead of conda",
)
def install(libraries, pip):
    """
    Install a new conda package by first adding it to environment.yml and then updating the environment. If called with no packages, will update the environment from environment.yaml instead.
    """
    if len(libraries) == 0:
        if not Path("./env").exists():
            call(
                "conda env create --prefix ./env --file environment.yml -q", shell=True
            )
            click.echo("environment packages installation complete!")
            click.echo("Acivate the environment with: conda activate ./env")
    else:
        # Convert multi-arg tuple to list; for some weird reason list() doesn't work
        libraries = [e for e in libraries]
        with open("environment.yml", "r+") as f:
            envdict = yaml.load(f, Loader=yaml.FullLoader)
        currentpip, everythingelse = split_conda_pip(envdict["dependencies"])
        if pip:
            merged = libraries + currentpip
            merged = set(merged)
            merged = [e for e in merged]

            pipdeps = {"pip": merged}
            everythingelse.append(pipdeps)
            # Check if pip is explicitly in deps otherwise add it
            # Nested check cause they could have pip>19, pip==20, etc
            if not any(["pip" in e for e in everythingelse]):
                everythingelse.append("pip")
            envdict["dependencies"] = everythingelse
        else:
            for e in libraries:
                if e not in envdict["dependencies"]:
                    envdict["dependencies"].append(e)
        with open("environment.yml", "w") as f:
            _ = yaml.dump(envdict, f, sort_keys=True)
        call(
            "conda env update --prefix ./env --file environment.yml  --prune -q",
            shell=True,
        )
        click.echo("environment packages updated")


if __name__ == "__main__":
    cli()
