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
import shlex

# Project imports
from env import Env,EnvVariable
from basheval import BashEval

class ModfileParser:
    def __init__(self, env=Env(), basheval=BashEval()):
        # Save arguments
        self.env = env
        self.be = basheval

        # Init commands
        self.commands = dict()
        self.init_commands()

        # Init other members
        self.do_unload = False

    def init_commands(self):
        self.commands['prepend_path'] = lambda *x: self.cmd_prepend_variable(
                *x, kind='path')
        self.commands['prepend_string'] = lambda *x: self.cmd_prepend_variable(
                *x, kind='string')
        self.commands['print'] = self.cmd_print
        self.commands['print_load'] = lambda *x: self.cmd_print(
                *x, unload=False)
        self.commands['print_unload'] = lambda *x: self.cmd_print(
                *x, load=False)

    def cmd_prepend_variable(self, name, value, kind='string'):
        if not self.env.variables.has_key(name):
            self.env.variables[name] = EnvVariable(name, kind=kind)
        self.env.variables[name].prepend(value, undo=self.do_unload)

    def cmd_append_variable(self, name, value, kind='string'):
        if not self.env.variables.has_key(name):
            self.env.variables[name] = EnvVariable(name, kind=kind)
        self.env.variables[name].append(value, undo=self.do_unload)

    def cmd_print(self, message, load=True, unload=True):
        if (load and not self.do_unload) or (unload and self.do_unload):
            self.be.echo(message)

    def load(self, modfile):
        self.do_unload = False
        return self.parse(modfile)

    def unload(self, modfile):
        self.do_unload = True
        return self.parse(modfile)

    def parse(self, modfile):
        if not os.path.isfile(modfile):
            return
        with open(modfile, 'r') as f:
            lines = f.readlines()
        try:
            for tokens in [shlex.split(line) for line in lines]:
                if len(tokens) == 0:
                    continue
                cmd = tokens[0]
                args = tokens[1:]
                if cmd in self.commands:
                    self.commands[cmd](*args)
            return True
        except Exception as e:
            self.be.error("Bad syntax in module file '{mf}': {e} ({n})".format(
                mf=modfile, e=e, n=type(e).__name__))
            return False

