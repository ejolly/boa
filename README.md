# Boa: The missing conda environment manager

Boa strives to be a CLI "wrapper" for [Anaconda](https://anaconda.org/) to make environment management a bit easier. It's heavily inspired by tools from the Javascript community likt [npm](https://www.npmjs.com/) or [yarn](https://yarnpkg.com/) which utilize a `package.json` file manage project dependencies. 

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Commands](#commands)
  - [init](#init)
  - [install](#install)
  - [config-autoenv](#config-autoenv)
- [Coming...](#coming)
  - [lockfile](#lockfile)
  - [uninstall](#uninstall)
  - [update](#update)
- [Limitations](#limitations)

## Overview

Boa's intended usage is to manage a conda environments in a **local**, completely encapsulated way within the working directory. This is accomplished by using `conda`'s [manage environment from file](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file) functionality.


The "blueprints" of your environment specifying Python and package versions are stored in an auto-updating `environment.yml` file (think `package.json` for Javascript folks). Actual conda packages are installed within a `env/` folder (think `node_modules` for Javascript folks). The benefits of this setup obviate the need for additional Python tools like `virtualenv` or [poetry](https://python-poetry.org/) (which currently only works with `pip` and `virtualenv`). The downside is that your `conda` environment is not available from any location on your computer, just the local working directory

## Installation

`pip install https://github.com/ejolly/boa.git`


## Usage

Boa treats `environment.yml` as it's "source of truth" for what `conda` packages to install and activate in an environment. You can always create, manage, and update this file by hand, but these things are precisely what Boa is designed to help with! 

Boa can create an initial minimal `environment.yml` using `boa init`, optionally requesting a specific Python version. Then you can run `boa install` which will "build" the environment by simply asking `conda` to install packages into a local `env` folder using `environment.yml`. 

You can add/remove packages by calling `boa install somepackage` or `boa uninstall somepackage`. Why do this instead of `conda install/uninstall` or `pip install/uninstall`? Simply because Boa will ensure that `environment.yml` is up-to-date after every operation. This ensures reproducibility and gives you (or others) the flexibility of easily deleting/resetting installed packaged (`boa clean`) and rebuilding and quickly environment. 

Boa also generates and stores an `environment-lock.yml` file which is the result of calling `conda env export --no-builds`. This file reflects *all* packages and dependencies in the current environment, ignoring platform-specific dependencies. Boa only uses this file to keep track of package version numbers and append them to `environment.yml`. In the event of any errors you can always create a new `conda` environment using this file directly to ensure reproducibility.

**Note:** *Boa will not know about packages you've install manually using* `conda install` or `pip install`! *Use `boa install` instead. It does the exact same thing but also keeps `environment.yml` up-to-date*

## Commands

You an always get a list of available commands and usage help with `boa --help` or `boa command --help`, e.g. `boa install --help`.


### init

`boa init [pythonversion]`  

Create a minimal `environment.yml` file in the current directory with nothing more than a `pythonversion` and Boa itself as dependencies. `pythonversion` should be a string, e.g. `'python=3.8'`. Defaults to `python=3.6`.  

*Insipiration:* `npm init`

### install

`boa install [PGK1] [PKG2] [--pip]`

If run with no arguments, builds a new environment from `environment.yml`. Otherwise behaves like `conda install` or `pip install` (when using the `--pip` flag) for installing one or more packages. Boa will automatically updated `environment.yml` for newly added packages. 

*Insipiration:* `npm install`

### config-autoenv

`boa config-autoenv`

Because it's not trivial to reliably call `conda activate` and `conda deactivate` from within a Python program, Boa instead offers a tool for *automatically* activating/deactivate environments if it detects the presences of an `environment.yml` file in the current directory. This works seamlessly as your `cd` in and out of folders on your computer, and will always print a message to let you know when an environment was auto-activated or deactivated. Calling this command will append a `source boa_autoenv.sh` to your `~/.zshrc` file. You can remove this line to disable auto activation/deactivation.

**Note:** `autoenv` *will activate local conda environments regardless of whether a project was initialized with* `boa init`. *It only cares about the presence of an* `environment.yml` *file in the working directory. If no `env` folder of installed packages exists, boa will try to automatically build this environment prior to auto-activation.*

---

## Coming...

### lockfile

An `environment.lock` which contains the exact locally installed package versions.

### uninstall

`boa uninstall`

### update

`boa update [PKG]`

---

## Limitations
Currently activating and deactivating an environment from within boa doesn't seem possible. So as a potentially more convenient work around checked out the `conda_auto_env.sh` file in this repo. If you `source` that in your `.zshrc` conda will auto activate an environment as soon as you `cd` into a folder with an `environment.yml` file and will auto-deactivate that environment as soon as you `cd` elsewhere. Pretty handy!
