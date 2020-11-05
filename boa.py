#!/Users/Esh/anaconda3/bin/python
"""
Main CLI run time
"""

from pathlib import Path
import click
from subprocess import call
import yaml

# import subprocess
# import os


@click.group()
def cli():
    pass


@cli.command()
@click.argument("name", required=False)
@click.argument("pyv", required=False)
@click.option(
    "--activate/--no-activate",
    default=True,
    help="auto-activate conda environment on creation",
)
@click.option(
    "--install/--no-install",
    default=True,
    help="auto-build the environment and save dependencies to ./env",
)
def init(name, pyv, activate, install):
    """
    Create an environment.yml in the local directory with name = [NAME] and python version = [PYV].\n

    NAME: name of the environment; only specified within the environment.yml; Default 'env'\n
    PYV: what python version to use; Default 'python=3.6'\n
    """

    if name is None:
        name = "env"
    if pyv is None:
        pyv = "python=3.6"
    env_file = Path("./environment.yml")
    if not env_file.exists():
        envdict = {
            "name": "null",
            "dependencies": [f"{pyv}", "pip", {"pip": ["git+https://github.com/ejolly/boa"]}],
        }
        with open("environment.yml", "w") as f:
            _ = yaml.dump(envdict, f, sort_keys=False)
        click.echo("created environment.yml")
    if install:
        if Path("./env").exists():
            click.echo(
                "env folder is already present. If you want to reinstall packages in environment.yml, delete it then cpm init"
            )
        else:
            call(
                "conda env create --prefix ./env --file environment.yml -q", shell=True
            )
            click.echo("environment packages installed into env/")
        click.echo("You need to manually activate: conda activate ./env")
    # if activate:
    #     myenv = os.environ.copy()
    #     subprocess.Popen('activate.sh', env=myenv)
    #     # os.system("source activate ./env")
    #     # call("source activate ./env", shell=True)
    #     click.echo("activated local environment")


@cli.command()
@click.argument("pkgs", nargs=-1)
@click.option("--skipinstall", is_flag=True, default=False, help="Just update environment.yml without actually rebuilding the environment")
def install(pkgs, skipinstall):
    """
    Install a new conda package by first adding it to environment.yml and then updating the environment.
    """
    with open("environment.yml", "r+") as f:
        envdict = yaml.load(f, Loader=yaml.FullLoader)
        envdict["dependencies"] = list(set(envdict["dependencies"] + list(pkgs)))
        f.seek(0)
        _ = yaml.dump(envdict, f, sort_keys=False)
        f.truncate()
    if not skipinstall:
        call(
            "conda env update --prefix ./env --file environment.yml  --prune",
            shell=True,
        )


if __name__ == "__main__":
    cli()
