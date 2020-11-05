#!/bin/bash

# conda-auto-env automatically activates a conda environment when
# entering a folder with an environment.yml file.
#
# If the environment doesn't exist, conda-auto-env creates it and
# activates it for you.
#
# To install add this line to your .bashrc or .bash-profile:
#
#       source /path/to/conda_auto_env.sh
#
# Modified from https://github.com/chdoig/conda-auto-env

function conda_auto_env() {
  # Check if you are already in the environment
  ACTIVE=$(echo $PATH | ggrep -s -o 'env' --no-messages)
  if [ -e "environment.yml" ]; then
    if [[ $ACTIVE != 'env' ]]; then
      # Try to activate the environment
      conda activate ./env
      if [ $? -eq 0 ]; then
        echo "Activated local conda env"
        :
      else
        # Create the environment and activate if it doesn't exist
        echo "Conda env doesn't exist, creating..."
        conda env create --prefix ./env --file environment.yml -q
        conda activate ./env
        echo "Auto-activated local conda env"
      fi
    fi
  else
    if [[ $ACTIVE == 'env' ]]; then
      echo "Auto-deactivated local conda env"
      conda deactivate
    fi
  fi
}

export PROMPT_COMMAND=conda_auto_env

chpwd_functions+=(conda_auto_env)
