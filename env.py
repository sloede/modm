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
    path_sep = ':'

    def __init__(self):
        # Load PATH to exepath
        self.exepath = (os.environ[self.exepath_var].split(self.path_sep) if
                os.environ.has_key(self.exepath_var) else [])
        if self.exepath == ['']:
            self.exepath = []

        # Load LD_LIBRARY_PATH to libpath
        self.libpath = (os.environ[self.libpath_var].split(self.path_sep) if
                os.environ.has_key(self.libpath_var) else [])
        if self.libpath == ['']:
            self.libpath = []

    def get_exepath_str(self):
        return Env.path_sep.join(self.exepath)

    def get_libpath_str(self):
        return Env.path_sep.join(self.libpath)
