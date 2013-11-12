#!/usr/bin/env python

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


# System imports
import os

class Env:
    """
    Class to handle environment variables in an easy way.
    """

    def __init__(self, modpath_var='MODM_MODULES_PATH',
                 modloaded_var='MODM_LOADED_MODULES'):
        """Save arguments and initialize variables for the module paths as well
        as the loaded modules.

        Arguments:
          modpath_var   -- environment variable for the modules path
          modloaded_var -- environment variable for the loaded modules
        """
        # Save arguments
        self.modpath_var = modpath_var
        self.modloaded_var = modloaded_var

        # Init other members
        self.modpath = self.load_path(modpath_var)
        self.modloaded = self.load_path(modloaded_var)
        self.variables = dict()

    def load_path(self, variable):
        """Load a environment variable and return it as a list of paths."""
        path = self.load_string(variable)
        return path.split(os.path.pathsep) if path else []

    def load_string(self, variable):
        """Load a environment variable and return it as a string."""
        return os.environ[variable] if variable in os.environ else None

    def get_modloaded_str(self):
        """Return loaded modules as a single string."""
        return os.path.pathsep.join(self.modloaded)

    def add_loaded_module(self, module):
        """Add `module` to the list of loaded modules."""
        self.modloaded.append(module)

    def remove_loaded_module(self, module):
        """Remove `module` from list of loaded modules if present."""
        if module in self.modloaded:
            self.modloaded.remove(module)


class EnvVariable:
    """
    Class to represent an environment variable.

    Allows easy handling (i.e. setting, getting, appending, prepending etc.)
    of environment variables of string and path type.
    """

    kinds = ['string', 'path']

    def __init__(self, name, kind='string'):
        """Set name and kind of variable, and load value if it exists.

        Arguments:
          name -- name of variable
          kind -- kind of variable (may be 'string' or 'path')
        """
        # Save arguments
        self._name = name
        self._kind = kind

        # Init value
        self._value = None
        self.load()

        # Init other members
        self._modified = False
        self._unset = False

    def load(self):
        """Load variable from environment if it exists."""
        # Set value if environment variable exists
        self._value = (os.environ[self._name] if self._name in os.environ
                       else None)
        # If variable exists and is a path, split it into individual paths
        if self._value is not None and self._kind == 'path':
            self._value = (self._value.split(os.path.pathsep) if self._value
                           else [])

    def is_set(self):
        """Return true if the variable has been set."""
        return True if self._value is not None else False

    def is_modified(self):
        """Return true if the variable was modified since creation."""
        return self._modified

    def is_unset(self):
        """Return true if this value was marked to be unset."""
        return self._unset

    def get_name(self):
        """Get name of variable."""
        return self._name

    def get_value(self):
        """Get value of variables (path variables are returned as strings)."""
        # If variable is not set, return None
        if not self.is_set():
            return None
        # If it is a path variable, return as string, otherwise return as string
        if self._kind == 'path':
            return os.path.pathsep.join(self._value)
        else:
            return self._value

    def get_export(self):
        """Return name, value tuple that can be used to export the variables."""
        return self.get_name(), self.get_value()

    def init_variable(self):
        """Initialize variable to be prepared for usage."""
        # If variable was already set, just return
        if self.is_set():
            return
        # Otherwise initialize it as a path or string variable
        elif self._kind == 'path':
            self._value = []
        else:
            self._value = ''
        # Mark variable as modified
        self._modified = True

    def prepend(self, value, undo=False):
        """Prepend string or path to variable.

        If `undo` is true, remove string/path from beginning of variable.
        """
        self.init_variable()
        # If not undo, prepend
        if not undo:
            if self._kind == 'path':
                self._value.insert(0, value)
            else:
                self._value = value + self._value
        # If undo, remove from beginning
        else:
            if self._kind == 'path':
                # If path is found in list, remove first occurrence
                if value in self._value:
                    self._value.remove(value)
            else:
                self._value = self._value.replace(value, '', 1)
        # Mark variable as modified
        self._modified = True

    def append(self, value, undo=False):
        """Append string or path to variable.

        If `undo` is true, remove string/path from end of variable.
        """
        self.init_variable()
        # If not undo, append
        if not undo:
            if self._kind == 'path':
                self._value.append(value)
            else:
                self._value = self._value + value
        # If undo, remove from end
        else:
            if self._kind == 'path':
                # If path is found in list, remove last occurrence
                if value in self._value:
                    del self._value[-1-l[::-1].index(value)]
            else:
                self._value = ''.join(self._value.rsplit(value, 1))
        # Mark variable as modified
        self._modified = True

    def set_value(self, value):
        """Set variable value to `value` (do not consider variable kind)."""
        self.init_variable()
        self._value = value
        self._modified = True

    def unset(self):
        """Mark variable as unset."""
        self._unset = True
        self._modified = True
