# Boa: The missing conda environment manager

Boa strives to be a CLI "wrapper" for [Anaconda](https://anaconda.org/) to make it behave a bit like how [npm](https://www.npmjs.com/) or [yarn](https://yarnpkg.com/) manage javascript modules with a`package.json` files. 

## Usage

`boa init [NAME] [PYV]`  

Will create an `environment.yml` file in the current directory and use it to install dependencies into `env/` in the current directory. For the time being you will have to manually activate the environment with `conda activate ./env`, or you can put `source conda_auto_env.sh` into your `.zshrc` to use zsh hooks to auto-activate/deactivate environments when you cd in or out of folders that have a `environment.yml` file.
