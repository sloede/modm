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


# Current Modm version
modm_version = 'v0.1+x'

# System imports
import sys
import os

# Project imports
from basheval import BashEval
from env import Env
from module import Module

def main():
    Modm(sys.argv, modm_version).run()

class Modm:
    help_file_suffix = '.txt'
    help_file_dir = 'doc'
    module_help_file = '.help'
    module_default_file = '.default'
    modules_path_var = 'MODM_MODULES_PATH'
    modules_loaded_var = 'MODM_LOADED_MODULES'
    admin_email_var = 'MODM_ADMIN_EMAIL'
    admin_default_email = 'root@localhost'

    def __init__(self, argv, version='<unknown>'):
        # Save arguments
        self.argv = argv
        self.version = version

        # Init other members
        self.be = BashEval()
        self.admin_email = os.environ[self.admin_email_var] if (
                os.environ.has_key(self.admin_email_var)) else (
                        self.admin_default_email)
        self.cmd = None
        self.args = []
        self.env = None
        self.modules = []

        # Set init variables to False
        self.is_init_argv = False
        self.is_init_env = False
        self.is_init_modules = False

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
        if not self.is_init_argv:
            self.cmd = self.argv[1] if len(self.argv) > 1 else None
            self.args = self.argv[2:] if len(self.argv) > 2 else []
            self.is_init_argv = True

    def init_env(self):
        if not self.is_init_env:
            self.env = Env(modpath_var=self.modules_path_var,
                    modloaded_var=self.modules_loaded_var)
            self.is_init_env = True

    def init_modules(self):
        self.init_env()

        # Iterate over directories containing the modules
        for modules_directory in self.env.modpath:
            # Iterate over module folders 
            for name in [d for d in os.listdir(modules_directory) if
                    os.path.isdir(os.path.join(modules_directory, d))]:
                # Get index
                index = self.find_module(name)
                if index == None:
                    self.modules.append(Module())
                    index = len(self.modules) - 1
                # Set name
                if self.modules[index].name is None:
                    self.modules[index].name = name
                # Set versions
                modpath = os.path.join(modules_directory, name)
                for modfile in [os.path.join(modpath, f) for f in
                        os.listdir(modpath) if
                        os.path.isfile(os.path.join(modpath, f))]:
                    if os.path.basename(modfile) == self.module_default_file:
                        # Set default version
                        if self.modules[index].default is None:
                            defaultversion = ''
                            with open(versionfile, 'r') as f:
                                defaultversion = f.read().strip()
                            defaultversionfile = os.path.join(modpath,
                                    defaultversion)
                            if os.path.isfile(defaultversionfile):
                                self.modules[index].default = defaultversionfile
                    elif os.path.basename(modfile) == self.module_help_file:
                        # Set help file
                        if self.modules[index].help_file is None:
                            self.modules[index].help_file = (
                                os.path.join(modpath, self.module_help_file))
                    else:
                        # Add version file
                        if os.path.basename(modfile) not in [os.path.basename(v)
                                for v in self.modules[index].versions]:
                            self.modules[index].versions.append(modfile)

        # Sort modules
        self.modules = sorted(self.modules, cmp=lambda x,y: cmp(x.name, y.name))
        # Sort versions
        for i in range(len(self.modules)):
            self.modules[i].versions = sorted(self.modules[i].versions,
                    cmp=lambda x,y: cmp(os.path.basename(x),
                        os.path.basename(y)))

    def find_module(self, name):
        head, tail = os.path.split(name)
        name = tail if head == '' else head
        for i, module in enumerate(self.modules):
            if module.name == name:
                return i
        return None

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
            self.print_help(os.path.join('commands', 'help'))
        elif topic in ['avail']:
            self.print_help(os.path.join('commands', 'avail'))
        elif topic in ['list']:
            self.print_help(os.path.join('commands', 'list'))
        elif topic in ['load']:
            self.print_help(os.path.join('commands', 'load'))
        elif topic in ['unload']:
            self.print_help(os.path.join('commands', 'unload'))
        else:
            self.be.error("Unknown help topic '{t}'.".format(t=topic))
            self.be.error("See 'modm help help' for a list of help topics.")

    def cmd_version(self):
        self.be.echo("modm version {v}".format(v=self.version))

    def cmd_avail(self):
        self.init_modules()
        for module in self.modules:
            for version in module.versions:
                self.be.echo(os.path.join(module.name,
                    os.path.basename(version)))

    def cmd_list(self):
        self.init_modules()
        pass

    def cmd_load(self):
        self.init_modules()
        pass

    def cmd_unload(self):
        self.init_modules()
        pass


# Run this script only if it is called directly
if __name__ == '__main__':
    main()
