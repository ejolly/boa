# Boa: The missing conda environment manager

*Contributors wanted!*

Boa strives to be a CLI "wrapper" for [Anaconda](https://anaconda.org/) to make environment management a bit easier. It's heavily inspired by tools from the Javascript community like [npm](https://www.npmjs.com/) or [yarn](https://yarnpkg.com/) which utilize a `package.json` file to manage project dependencies. Currently only compatible with `zsh`. Checkout the demo GIF for an overview of it's current functionality:   

![](boa.gif)

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Commands](#commands)
  - [setup](#setup)
  - [init](#init)
  - [install](#install)
  - [uninstall](#uninstall)
  - [link](#link)
  - [unlink](#unlink)
- [Additional Info](#additional-info)
  - [lockfile](#lockfile)
- [Roadmap](#roadmap)

## Overview

Boa's intended usage is to manage a conda environment in a **local**, completely encapsulated way within the working directory. This is accomplished by using `conda`'s [manage environment from file](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file) functionality.


The "blueprints" of your environment specifying Python and package versions are stored in an auto-updating `environment.yml` file (think `package.json` for Javascript folks). Actual conda packages are installed within a `env/` folder (think `node_modules` for Javascript folks). The benefits of this setup obviates the need for additional Python tools like `virtualenv` or [poetry](https://python-poetry.org/) (which currently only works with `pip` and `virtualenv`). The downside is that your `conda` environment is not available from any location on your computer, just the local working directory. You can always create, manage, and updated an `environment.yml` file by hand, but this is precisely what Boa is designed to help with!

## Installation

`pip install git+https://github.com/ejolly/boa.git`  
`boa setup --autoenv`  (using `--autoenv` is highly recommended but see the [caveats](#autoenv-caveats) below!)


## Usage

Boa can create an initial minimal `environment.yml` using `boa init`, optionally requesting a specific Python version. Then you can run `boa install` which will "build" the environment by simply asking `conda` to install packages into a local `env` folder using `environment.yml`. 

You can add/remove packages by calling `boa install somepackage` or `boa uninstall somepackage`. Why do this instead of `conda install/uninstall` or `pip install/uninstall`? Simply because Boa will ensure that `environment.yml` is up-to-date after every operation. This ensures reproducibility and gives you (or others) the flexibility of easily deleting/resetting installed packaged (`boa clean`) and rebuilding and environment quickly. 

**Note:** *Presently Boa will not know about packages you've install manually using* `conda install` or `pip install`!  
*Use `boa install` instead! It does the exact same thing but also keeps `environment.yml` up-to-date*

## Commands

You an always get a list of available commands and usage help with `boa --help` or `boa command --help`, e.g. `boa install --help`.


### setup

`boa setup [--autoenv]`

You should run this the first time you install Boa, preferablly using the `--autoenv` flag. This will add the following command aliases to your `~/.zshrc`: `boa-activate` and `boa-deactivate` which behave just like `conda activate/deactivate` but for the local environment (note the `-`). The `--autoenv` flag will setup a hook to **automatically activate and deactivate** a local environment when you `cd` into a directory that contains an `environment.yml` file. Setting up Boa with this functionality is recommended as boa will seamlessly handle switching conda environments for you as your `cd` around. 

#### autoenv caveats

`--autoenv` only cares about the presence of `environment.yml` in the local directory and it doesn't care if this file was created using Boa (`boa init`) or manually. If it detects such a file and an `env` folder in the same directory, it will try to automatically activate the environment. If no `env` folder is present, Boa will automatically build the environment using the `environment.yml` file. If you're already using `environment.yml` in your projects you may not want these automatic behaviors, hence why the flag is optional. You can always use `conda activate/deactivate` or the equivalent `boa-activate`/`boa-deactivate` (note the `-`) to change environments if boa has auto-switched for you.

### init

`boa init [pythonversion]`  

Create a minimal `environment.yml` file in the current directory with nothing more than a `pythonversion` and Boa itself as dependencies. `pythonversion` should be a string, e.g. `'python=3.8'`. Defaults to `python=3.6`.  

*Insipiration:* `npm init` and `package.json`

### install

`boa install [PGK1] [PKG2]... [--pip]`

If run with no arguments, builds a new environment from `environment.yml`. Otherwise behaves like `conda install` or `pip install` (when using the `--pip` flag) for installing one or more packages. Boa will automatically update `environment.yml` for newly added packages. 

*Insipiration:* `npm install`

### uninstall

`boa uninstall PGK1 [PKG2]... [--pip]`

Uninstall a package in the current environment. Behaves like `conda uninstall` or `pip uninstall` (when using the `--pip` flag), but also removes the package from `environment.yml`. 

### link

`boa link`

Makes the current local Boa environment available for use in your base `conda` environment. Linking allows you to use your base environment to create notebooks hooked up to *other environments*, without having to `cd` to a particular folder or `conda activate` anything. You can do this by starting a `jupyter notebook/lab` server from your base environment, and using the drop down *kernel select* menu when creating a new notebook. Boa will name the kernel for this environment after the folder than contains the `environment.yml` (`project` in the GIF above). This is convenient because it only requires you to have **one** working `jupyter notebook/lab` installation in your base environment, rather than repeatedly adding `jupyter` and it's dependencies to each new `environment.yml`. Instead Boa will add a single `ipykernel` dependency and configure it for you.  

### unlink

`boa unlink`

Undoes a link, uninstalls `ipykernel` from the local environment, and removes it from `environment.yml`.


## Additional Info  

### lockfile  

`conda` doesn't have an exact equivalent of a `package-lock.json` file which in Javascript-land is auto-updating file that keeps track of the *exact* package versions installed, plus all their dependencies. Boa approximates this by creating an `environment-lock.yml` via the `conda env export --no-builds` command after any operation. This file reflects *all* packages and dependencies in the current environment, ignoring platform-specific dependencies. 

What is the point of this file? In short, it allows Boa to update package versions in `environment.yml`. It also provides the most update-to-date characterization of the current `conda` environment. Feel free to put this file under version control. You can even pass it to `conda` directly to bootstrap a new environment in a platform-independent way without using Boa: `conda env create --file environment-lock.yml`

*Insipiration:* `package-lock.json`

---

## Roadmap

- `boa update`
- conda channel support

