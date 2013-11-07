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


import os

class Env:
    exepath_var = 'PATH'
    libpath_var = 'LD_LIBRARY_PATH'

    def __init__(self, modpath_var='MODM_MODULES_PATH',
            modloaded_var='MODM_LOADED_MODULES'):
        # Save arguments
        self.modpath_var = modpath_var
        self.modloaded_var = modloaded_var

        # Init other members
        self.exepath = self.load_path(self.exepath_var)
        self.libpath = self.load_path(self.libpath_var)
        self.modpath = self.load_path(modpath_var)
        self.modloaded = self.load_path(modloaded_var)

    def load_path(self, variable):
        path = self.load_string(variable)
        return path.split(os.path.pathsep) if path else []

    def load_string(self, variable):
        return os.environ[variable] if os.environ.has_key(variable) else None

    def get_exepath_str(self):
        return os.path.pathsep.join(self.exepath)

    def get_libpath_str(self):
        return os.path.pathsep.join(self.libpath)

    def get_modloaded_str(self):
        return os.path.pathsep.join(self.modloaded)

    def add_loaded_module(self, module):
        self.modloaded.append(module)

    def remove_loaded_module(self, module):
        if module in self.modloaded:
            self.modloaded.remove(module)

class EnvVariable:
    kinds = ['string', 'path']
    def __init__(self, name, kind='string'):
        # Save arguments
        self._name = name
        self._kind = kind

        # Init value
        self._value = None
        self.load()

        # Init other members
        self._modified = False

    def load(self):
        self._value = os.environ[_name] if os.environ.has_key(_name) else None
        if self._value is not None and self._kind == 'path':
            self._value = self._value.split(os.path.pathsep) if self._value else []

    def is_set(self):
        return True if self._value is not None else False

    def is_modified(self):
        return self._modified

    def get_name(self):
        return self._name

    def get_value(self):
        if self._value is None:
            return None
        if self._kind == 'path':
            return os.path.pathsep.join(self._value)
        else:
            return self._value

    def get_export(self):
        return (self.self.get_name(), self.get_value())

    def init_variable(self):
        if self._value is not None:
            return
        if self._kind == 'path':
            self._value = []
        else:
            self._value = ''
        self._modified = True

    def prepend(self, value, undo=False):
        self.init_variable()
        if not undo:
            if self._kind == 'path':
                self._value.insert(0, value)
            else:
                self._value = value + self._value
        else:
            if self._kind == 'path':
                if value in self._value:
                    self._value.remove(value)
            else:
                self._value = self._value.replace(value, '', 1)
        self._modified = True

    def append(self, value, undo=False):
        self.init_variable()
        if not undo:
            if self._kind == 'path':
                self._value.append(value)
            else:
                self._value = self._value + value
        else:
            if self._kind == 'path':
                if value in self._value:
                    del self._value[-1-l[::-1].index(value)]
            else:
                self._value = ''.join(self._value.rsplit(value, 1))
        self._modified = True
