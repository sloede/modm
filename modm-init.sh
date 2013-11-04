#!/bin/bash

################################################################################
# Modm - Modules iMproved
################################################################################

# Set full path to modm.py
MODM_PY=/home/mic/Code/modm/modm.py

################################################################################
# NO NEED TO EDIT ANYTHING BEYOND THIS POINT
################################################################################

# Execution guard - this file needs to be sourced!
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  echo "*** ERROR: Script '$0' was executed (must be sourced)."
  exit 2
fi

# Define function to call MODM and make it available to subshells
modm() {
  eval "`$MODM_PY \"$@\"`"
}
export -f modm
export MODM_PY
