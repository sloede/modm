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
        self.exepath = self.load_path_var(self.exepath_var)
        self.libpath = self.load_path_var(self.libpath_var)
        self.modpath = self.load_path_var(modpath_var)
        self.modloaded = self.load_path_var(modloaded_var)

    def load_path_var(self, variable):
        path = self.load_text_var(variable)
        return path.split(os.path.pathsep) if path else []

    def load_text_var(self, variable):
        return os.environ[variable] if os.environ.has_key(variable) else None

    def get_exepath_str(self):
        return os.path.pathsep.join(self.exepath)

    def get_libpath_str(self):
        return os.path.pathsep.join(self.libpath)
