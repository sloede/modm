#!/bin/bash

# Modm - Modules iMproved
# Copyright (C) 2013  Michael Schlottke
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


# Set global configuration values for Modm (all variables will be export'd)

# Set full path to modm.py
MODM_PY=/home/mic/Code/modm/modm.py

# Set path to module file directory(s)
MODM_MODULES_PATH="/home/mic/.pool/modm-modules"

# Set email address to show for internal error messages
MODM_ADMIN_EMAIL="root@localhost"


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
  eval "`$MODM_PY $*`"
}

# Export functions and Modm configuration values
export -f modm
export MODM_PY
export MODM_MODULES_PATH
export MODM_ADMIN_EMAIL
