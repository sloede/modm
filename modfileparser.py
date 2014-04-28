#!/usr/bin/env python

# Modm - Modules iMproved
# Copyright (C) 2013-2014  Michael Schlottke
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
    """
    Class to parse module files and execute commands found in them.
    """

    backup_prefix = 'MODM_BACKUP_'

    def __init__(self, env=Env(), basheval=BashEval()):
        """Save arguments to class and initialize list of valid commands.

        Arguments:
          env      -- object to handle environment variables
          basheval -- object to convert commands to Bash evaluation strings
        """
        # Save arguments
        self.env = env
        self.be = basheval

        # Init commands
        self.commands = dict()
        self.init_commands()

        # Init other members
        self.do_unload = False

    def init_commands(self):
        """Initialize all commands that are supported in module files."""
        self.commands['prepend_path'] = lambda *x: self.cmd_prepend_variable(
                *x,
                kind='path')
        self.commands['prepend_string'] = lambda *x: self.cmd_prepend_variable(
                *x,
                kind='string')
        self.commands['print'] = self.cmd_print
        self.commands['print_load'] = lambda *x: self.cmd_print(
                *x,
                unload=False)
        self.commands['print_unload'] = lambda *x: self.cmd_print(
                *x,
                load=False)
        self.commands['set'] = self.cmd_set

    def cmd_prepend_variable(self, name, value, kind='string'):
        """Prepend variable `name` with `value`."""
        # Create variable if it does not exist yet
        if not name in self.env.variables:
            self.env.variables[name] = EnvVariable(name, kind=kind)

        # Prepend value (or undo prepend)
        self.env.variables[name].prepend(value, undo=self.do_unload)

    def cmd_append_variable(self, name, value, kind='string'):
        """Append variable `name` with `value`."""
        # Create variable if it does not exist yet
        if not name in self.env.variables:
            self.env.variables[name] = EnvVariable(name, kind=kind)

        # Append value (or undo append)
        self.env.variables[name].append(value, undo=self.do_unload)

    def cmd_print(self, message, load=True, unload=True):
        """Print `message`."""
        if (load and not self.do_unload) or (unload and self.do_unload):
            self.be.echo(message)

    def cmd_set(self, name, value):
        """Set variable `name` to `value`.

        Save backup of `name` if it exists already, and restore the
        original value upon unloading.
        """
        # Create variable if it does not exist yet
        if not name in self.env.variables:
            self.env.variables[name] = EnvVariable(name)

        # Determine name of potential backup variable and create backup variable
        # if it does not exist
        backupname = self.backup_prefix + name
        if backupname not in self.env.variables:
            self.env.variables[backupname] = EnvVariable(backupname)

        # If variable is to be set, check if it is already set and save backup
        if not self.do_unload:
            if self.env.variables[name].is_set():
                self.env.variables[backupname].set_value(
                        self.env.variables[name].get_value())
            self.env.variables[name].set_value(value)
        # If variable is to be unset, check if backup variable exists and
        # restore it
        else:
            if self.env.variables[backupname].is_set():
                self.env.variables[name].set_value(
                        self.env.variables[backupname].get_value())
                self.env.variables[backupname].unset()
            else:
                self.env.variables[name].unset()

    def load(self, modfile):
        """Load module file `modfile`."""
        self.do_unload = False
        return self.parse(modfile)

    def unload(self, modfile):
        """Unload module file `modfile`."""
        self.do_unload = True
        return self.parse(modfile)

    def parse(self, modfile):
        """Parse module file `modfile` and execute commands that are found.

        Return true if parsing was successful, otherwise false."""
        # Return without doing anything if file is not found
        if not os.path.isfile(modfile):
            return

        # Read module file
        with open(modfile, 'r') as f:
            lines = f.readlines()

        # Try to parse each line into shell tokens or die
        try:
            splitlines = [shlex.split(line) for line in lines]
        except Exception as e:
            self.be.error("Bad syntax in module file '{mf}': {e} ({n})".format(
                    mf=modfile, e=e, n=type(e).__name__))
            return False

        # Parse each line indicidually
        for tokens in splitlines:
            # Skip line if there were no tokens
            if len(tokens) == 0:
                continue

            # First token is command, rest (if existing) are arguments
            cmd = tokens[0]
            args = tokens[1:]

            # If command exists, execute it while providing the arguments from
            # the file
            if cmd in self.commands:
                self.commands[cmd](*args)

        # Return true to indicate that nothing was wrong
        return True

