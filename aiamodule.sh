#!/bin/bash

################################################################################
# AIAMODULE
################################################################################

# Set initial configuration

# Directory with module information
MODULES_DIR=/home/mic/Code/aiamodule/modules

# Module default file name
DEFAULT_MODULE=default

################################################################################
# NO NEED TO EDIT ANYTHING BEYOND THIS POINT
################################################################################

# Display error message
function errormsg {
  echo "*** ERROR: $1"
}

# Execution guard - this file needs to be sourced!
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  errormsg "Script was executed (must be sourced)."
  exit 2
fi

function aiamodule_help {
  echo hhhelp
}

function aiamodule_avail {
  for modpath in $MODULES_DIR/*; do
    modname=`basename $modpath`
    for modversionpath in $modpath/*; do
      modversion=`basename $modversionpath`
      echo $modname/$modversion
    done
  done
}

# Parse command
usercmd="$1"
if [ -z "$usercmd" ]; then
  usercmd=help
fi
shift

case $usercmd in 
  avail)
    aiamodule_avail "$@"
    ;;

  list)
    aiamodule_list "$@"
    ;;

  load)
    aiamodule_load "$@"
    ;;

  unload)
    aiamodule_unload "$@"
    ;;

  help)
    aiamodule_help
    ;;

  *)
    errormsg "'$usercmd' is not a valid command."
    errormsg "Try running 'aiamodule help' for usage information."
    return 2
    ;;
esac

