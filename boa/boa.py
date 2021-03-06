"""
Main CLI run time
"""

from pathlib import Path
import click
from subprocess import CalledProcessError, call, check_output
import yaml
import shutil
import os
import sys


def check_for_package(pkg, somelist):
    """Return a subset of elements in somelist that contain pkg='"""
    hasit = [e for e in somelist if f"{pkg}=" in e]
    nohasit = [e for e in somelist if f"{pkg}=" not in e]
    return hasit, nohasit


def verify_install(pkg, pip):
    """Verify a package was actually installed"""
    try:
        if pip:
            _ = check_output(f"pip list | grep {pkg}", shell=True)
        else:
            _ = check_output(f"conda list | grep {pkg}", shell=True)
        return True
    except CalledProcessError as e:  # noqa
        return False


def env_isactive():
    cwd = os.getcwd()
    current_py = check_output("which python", shell=True)
    if cwd in str(current_py):
        return True
    else:
        return False


def run(cmd):
    """Run a command a shell that has the local environment activate"""
    if env_isactive():
        call(cmd, shell=True)
    else:
        call(f"/bin/zsh -i -c 'boa-activate && {cmd} && exit'", shell=True)
    return


def version_deps_and_make_lockfile(libraries=None, pip=False, uninstall=False):
    """Update package versions from environment-lock.yml"""

    run("conda env export --no-builds -f environment-lock.yml")
    with open("environment-lock.yml", "r") as f:
        envlockdict = yaml.load(f, Loader=yaml.FullLoader)

    with open("environment.yml", "r") as f:
        envdict = yaml.load(f, Loader=yaml.FullLoader)

    lockdeps_pip, lockdeps_else = split_conda_pip(envlockdict["dependencies"])
    currentdeps_pip, currentdeps_else = split_conda_pip(envdict["dependencies"])
    versioned_deps, versioned_pipdeps = [], []
    if uninstall:
        # Prune out deps
        if pip:
            for e in libraries:
                _, nohasit = check_for_package(e, currentdeps_pip)
                versioned_pipdeps += nohasit
            versioned_pipdeps = set(versioned_pipdeps)
            versioned_pipdeps = [e for e in versioned_pipdeps]
            versioned_deps = currentdeps_else
        else:
            for e in libraries:
                _, nohasit = check_for_package(e, currentdeps_else)
                versioned_deps += nohasit
            versioned_deps = set(versioned_deps)
            versioned_deps = [e for e in versioned_deps]
            versioned_pipdeps = currentdeps_pip
    else:
        # For anything in the environment.yml that doesn't have a version, get it from the lock (exported env) file
        for dep in currentdeps_else:
            depversion, _ = check_for_package(dep, lockdeps_else)
            if depversion:
                versioned_deps.append(depversion[0])
            else:
                versioned_deps.append(dep)
        for dep in currentdeps_pip:
            depversion, _ = check_for_package(dep, lockdeps_pip)
            if depversion:
                versioned_pipdeps.append(depversion[0])
            else:
                versioned_pipdeps.append(dep)
        # Add versioned numbers for recently installed packages
        if libraries is not None:
            to_check = currentdeps_pip if pip else currentdeps_else
            to_get = lockdeps_pip if pip else lockdeps_else
            to_update = versioned_pipdeps if pip else versioned_deps
            for lib in libraries:
                hasit, _ = check_for_package(lib, to_check)
                if not hasit:
                    hasit, _ = check_for_package(lib, to_get)
                    try:
                        to_update.append(hasit[0])
                    except IndexError as e:  # noqa
                        click.echo(
                            "Updating environment.yml failed. Was the requested pkg(s) already installed via --pip or as dependency of another package?"
                        )
    # Update file
    versioned_deps.append({"pip": versioned_pipdeps})
    envdict["dependencies"] = versioned_deps
    with open("environment.yml", "w") as f:
        _ = yaml.dump(envdict, f, sort_keys=True)


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
@click.option("--autoenv", is_flag=True, default=False)
def setup(autoenv):
    """
    Install Boa shell tools. By default adds commands to your .zshrc to activate and deactive conda environments. Can optionally setup an autoenv hook that will auto-activate/deactivate environments if an environment.yml file is present in the current directory.
    """
    shell = os.environ["SHELL"]
    path = Path()
    if "zsh" in shell:
        path = path.home().joinpath(".zshrc")
    else:
        raise ValueError("Boa auto-env only supports zsh")
    if path.exists():
        try:
            with open(path, "a") as f:
                f.write("\n# >>> boa start >>>\n")
                f.write("alias boa-activate='conda activate ./env'\n")
                f.write("alias boa-deactivate='conda deactivate'\n")
                if autoenv:
                    f.write("source boa_autoenv.sh\n")
                    msg = f"Succesfully modified {str(path)} to add boa shell tools with auto-environment activation"
                else:
                    msg = f"Succesfully modified {str(path)} to add boa shell tools"
                f.write("# <<< boa end <<<\n")
            click.echo(msg)
            click.echo(
                "You will need to reload your terminal or 'source ~/.zshrc' for this to take effect"
            )
            click.echo(
                f"To remove boa shell tools, just delete the block commented by boa start >>> and boa end <<< in {str(path)}"
            )
        except:
            click.secho("Unable to update your shell config file", color="red")
    else:
        raise FileNotFoundError(
            "Could not locate your shell config file. Do you have a .zshrc and is it stored somewher other than your home directory?"
        )


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
        pyv = "python=3.8"
    env_file = Path("./environment.yml")
    if not env_file.exists():
        envdict = {
            "name": "null",
            "channels": ["defaults", "conda-forge"],
            "dependencies": [
                f"{pyv}",
                "pip",
                "conda-forge::mamba",
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
    if env_isactive():
        click.echo("Please first deactivate the current environment using boa-deactivate or conda deactivate")
    else:
        try:
            shutil.rmtree("./env")
            Path("./environment-lock.yml").unlink()
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
            try:
                check_output("which mamba", shell=True)
                run("mamba create --prefix ./env --file environment.yml -q --no-banner")
            except CalledProcessError as e:  # noqa
                call(
                    "conda env create --prefix ./env --file environment.yml -q",
                    shell=True,
                )
            version_deps_and_make_lockfile()
            click.echo("\nEnvironment setup and install complete!\n")
            click.echo("Future installs will be much faster thanks to mamba.\n")
            click.echo("Activate with boa-activate if you didn't run boa setup --autoenv. Otherwise just cd out of and back into the cwd.")
    else:
        libraries_str = " ".join(libraries)
        if pip:
            run(f"pip install {libraries_str} -q")
            version_deps_and_make_lockfile(libraries, pip)
        else:
            try:
                check_output("which mamba", shell=True)
                run(f"mamba install {libraries_str} -y -q --no-banner")
            except CalledProcessError as e:  # noqa
                run("conda env create --prefix ./env --file environment.yml -q")
            version_deps_and_make_lockfile(libraries, pip)

        statuses = [verify_install(lib, pip) for lib in libraries]
        if all(statuses):
            click.echo("\nPackage(s) installed successfully!")
        else:
            raise ValueError("Package installation not successful!")


@cli.command()
@click.pass_context
def link(ctx):
    """
    Make this local environment accessible by your base conda environmet. Linking will allow you use your local environment in a jupyter notebook running from your base environment. This is convenient because it means you don't have to worry about installing jupyter in your local environment just to be able to use it interactively. This works by installing and configuring a single package in your local environment: ipykernel. Boa uses this to make your base conda environment "aware" of this environment and will name it after the current working directory.
    """
    try:
        ctx.invoke(install, libraries=["ipykernel"], pip=False)
        run("python -m ipykernel install --user --name $(basename $PWD)")
        click.echo("Link successful!")
        click.echo(
            f"If you start a jupyter notebook server from your base environment you should now see an option to create a notebook with the a kernel called: '{Path().cwd().stem}'."
        )
    except:
        click.echo(f"{sys.exc_info()[0]}")


@cli.command()
@click.pass_context
def unlink(ctx):
    """
    Unlink this local environment from your base conda environment (undoes a 'link'). This environment will no longer show up as an available kernel to use when creating new jupyter notebooks. Also removes ipykernel from the local environment.
    """
    try:
        call(
            "/bin/zsh -i -c 'jupyter kernelspec uninstall -f $(basename $PWD) && exit'",
            shell=True,
        )
        ctx.invoke(uninstall, libraries=["ipykernel"], pip=False)
        click.echo("Environment unlinked!")
    except:
        click.echo(f"{sys.exc_info()[0]}")


@cli.command()
@click.argument("libraries", nargs=-1, required=True)
@click.option(
    "--pip",
    is_flag=True,
    default=False,
    help="Assume uninstall should happen with pip instead of conda",
)
def uninstall(libraries, pip):
    """
    Uninstall a conda or pip package and remove it from environment.yml
    """

    libraries_str = " ".join(libraries)
    if pip:
        run(f"pip uninstall {libraries_str} -y -q")
        version_deps_and_make_lockfile(libraries, pip, uninstall=True)
    else:
        # Use conda to uninstall because it also removes some pkg deps which mamba doesn't
        run(f"conda uninstall {libraries_str} -y -q")
        version_deps_and_make_lockfile(libraries, pip, uninstall=True)

    statuses = [not verify_install(lib, pip) for lib in libraries]
    if all(statuses):
        click.echo("\nPackages uninstalled successfully!")
    else:
        raise ValueError("Package uninstallation not successful")


if __name__ == "__main__":
    cli()
