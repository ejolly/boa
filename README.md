# Boa: The missing conda environment manager

Boa strives to be a CLI "wrapper" for [Anaconda](https://anaconda.org/) to make it behave a bit like how [npm](https://www.npmjs.com/) or [yarn](https://yarnpkg.com/) manage javascript modules with a`package.json` files.

## Goal

Taking a cue from the Javascript world, Boa's intended usage is to manage a conda environments in a **local**, completely encapsulated way within the working directory. This is accomplished by using conda's [manage environment from file](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file) functionality.


The "blueprints" of your environment specifying versions and such are stored in an auto-updating `environment.yml` file (think `package.json` for Javascript folks). Actual conda package are installed within a `env/` folder (think `node_modules` for Javascript folks.

Currently activating and deactivating an environment from within boa doesn't seem possible. So as a potentially more convenient work around checked out the `conda_auto_env.sh` file in this repo. If you `source` that in your `.zshrc` conda will auto activate an environment as soon as you `cd` into a folder with an `environment.yml` file and will auto-deactivate that environment as soon as you `cd` elsewhere. Pretty handy!


## Installation

`pip install https://github.com/ejolly/boa.git`


## Usage

Boa works entirely from the command line. You can manually edit the `environment.yml` file by hand and boa will work with it just fine. Otherwise there are some commands Boa provides that essentially update this file and ultimately run some `conda` or `pip` commands. Currently the following commands are implemented. Optional arguments are specified with `[ARG]` while required arguments are specified as `ARG`.

*Boa will not know about packages you've install manually using `conda install` or `pip install`!*  

*Use `boa install` instead. It does the exact same thing but also keeps `environment.yml` up-to-date*

### Init

`boa init [pythonversion]`  

Create `environment.yml` file in the current directory with nothing more than a `pythonversion` and Boa itself as dependencies. `pythonversion` should be a string, e.g. `python=3.8`. Defaults to `python=3.6`.  

*Insipiration:* `npm init`

### Install

`boa install [PGK1] [PKG2] [--pip]`

Build a new environment from `environment.yml` if no arguments passed in. Otherwise install multiple new packages like `conda install`, but also add them to `environment.yml`, e.g. `boa install numpy pandas seaborn`. Use in the `--pip` flag to tell Boa that packages should be install using `pip` instead of `conda`.

*Insipiration:* `npm install`

---

## Coming...

### Lockfile

An `environment.lock` which contains the exact locally installed package versions.

### Uninstall

`boa uninstall`

### Update

`boa update [PKG]`
