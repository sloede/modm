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


# Set global configuration values for Modm

# Set email address to show in error messages
admin_email = 'root@localhost'

# Set name of environment variable with locations of modules
# Note: If you change this value, you also need to change the environment
#       variable in modm-init.sh.
modules_path_var = 'MODM_MODULES_PATH'

# Set name of environment variable with names of loaded modules
modules_loaded_var = 'MODM_LOADED_MODULES'


################################################################################
# NO NEED TO EDIT ANYTHING BEYOND THIS POINT
################################################################################

# Current Modm version
modm_version = 'v0.1+x'

# System imports
import sys
import os

# Project imports
from basheval import BashEval
from env import Env

def main():
    m = Modm(sys.argv, modules_path_var, modules_loaded_var,
            admin_email, modm_version)
    m.run()

class Modm:
    help_file_suffix = '.txt'
    help_file_dir = 'doc'

    def __init__(self, argv, modules_path_var='MODM_MODULES_PATH',
            modules_loaded_var='MODM_LOADED_MODULES',
            admin_email='root@localhost', version='<unknown>'):
        # Save arguments
        self.argv = argv
        self.modules_path_var = modules_path_var
        self.modules_loaded_var = modules_loaded_var
        self.admin_email = admin_email
        self.version = version
        self.cmd = None
        self.args = []

        # Init other members
        self.be = BashEval()
        self.env = Env()

    def run(self):
        try:
            self.rununsafe()
        except Exception as e:
            self.be.clear()
            self.be.error("An unknown error occurred.", internal=True)
            self.be.error("Please send an email with the command you used and "
                    + "the error message printed above to '{e}'."
                    .format(e=self.admin_email), internal=True)
            raise
        finally:
            sys.stdout.write(self.be.cmdstring())

    def rununsafe(self):
        self.init_argv()

        if self.cmd in ['help', '--help']:
            self.cmd_help()
        elif self.cmd in ['--version']:
            self.cmd_version()
        elif self.cmd in ['avail']:
            self.cmd_avail()
        elif self.cmd in ['list']:
            self.cmd_list()
        elif self.cmd in ['load']:
            self.cmd_load()
        elif self.cmd in ['unload']:
            self.cmd_unload()
        elif not self.cmd:
            self.be.error("No command given.")
            self.print_help('usage')
        else:
            arg_type = "Option" if self.cmd[0] == '-' else "Command"
            self.be.error("{t} '{c}' not recognized."
                    .format(t=arg_type, c=self.cmd))
            self.print_help('usage')

    def init_argv(self):
        self.cmd = self.argv[1] if len(self.argv) > 1 else None
        self.args = self.argv[2:] if len(self.argv) > 2 else []

    def print_help(self, topic):
        help_file = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                Modm.help_file_dir, topic + Modm.help_file_suffix)

        if os.path.isfile(help_file):
            with open(help_file, 'r') as f:
                self.be.echo(f.read(), newline=False)
        else:
            self.be.error("Help file '{f}' not found.".format(f=help_file),
                    internal=True)
            self.be.error("Please send an email with the command you used and "
                    + "the error message printed above to '{e}'."
                    .format(e=self.admin_email), internal=True)

    def cmd_help(self):
        topic = self.args[0] if len(self.args) > 0 else None
        if self.cmd in ['--help'] or topic is None:
            self.print_help('usage')
        elif topic in ['help']:
            self.print_help('commands/help')
        elif topic in ['avail']:
            self.print_help('commands/avail')
        elif topic in ['list']:
            self.print_help('commands/list')
        elif topic in ['load']:
            self.print_help('commands/load')
        elif topic in ['unload']:
            self.print_help('commands/unload')
        else:
            self.be.error("Unknown help topic '{t}'.".format(t=topic))
            self.be.error("See 'modm help help' for a list of help topics.")

    def cmd_version(self):
        self.be.echo("modm version {v}".format(v=self.version))


# Run this script only if it is called directly
if __name__ == '__main__':
    main()
