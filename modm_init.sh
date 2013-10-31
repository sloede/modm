#!/bin/bash

################################################################################
# AIAMODULE
################################################################################

# Set path to aiamodule.py
AIAMODULE_PY=/home/mic/Code/aiamodule/aiamodule.py

################################################################################
# NO NEED TO EDIT ANYTHING BEYOND THIS POINT
################################################################################

# Execution guard - this file needs to be sourced!
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  echo "*** ERROR: Script '$0' was executed (must be sourced)."
  exit 2
fi

# Define function to call AIAMODULE and make it available to subshells
aiamodule() {
  eval `$AIAMODULE_PY "$@"`
}
export -f aiamodule
export AIAMODULE_PY
