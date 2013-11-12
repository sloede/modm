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
__version__ = '0.3+x'

# System imports
import sys
import os

# Project imports
from basheval import BashEval
from env import Env
from module import Module
from natsort import natsorted
from modfileparser import ModfileParser

def main():
    Modm(sys.argv).run()

class Modm:
    help_file_suffix = '.txt'
    help_file_dir = 'doc'
    module_help_file = '.help'
    module_default_file = '.default'
    module_category_file = '.category'
    modules_path_var = 'MODM_MODULES_PATH'
    modules_loaded_var = 'MODM_LOADED_MODULES'
    admin_email_var = 'MODM_ADMIN_EMAIL'
    admin_default_email = 'root@localhost'
    available_commands = ['avail', 'status', 'help', 'list', 'load', 'unload']

    def __init__(self, argv=['modm.py']):
        # Save arguments
        self.argv = argv

        # Init other members
        self.be = BashEval()
        self.admin_email = os.environ[self.admin_email_var] if (
                self.admin_email_var in os.environ) else (
                        self.admin_default_email)
        self.cmd = None
        self.args = []
        self.env = None
        self.modules = []
        self.parser = None

        # Set init variables to False
        self.is_init_argv = False
        self.is_init_env = False
        self.is_init_modules = False
        self.is_init_parser = False

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
        command, alternatives = self.parse_command(self.cmd)

        if command in ['help', '--help']:
            self.cmd_help()
        elif command in ['--version']:
            self.cmd_version()
        elif command in ['avail', 'status']:
            self.cmd_avail()
        elif command in ['list']:
            self.cmd_list()
        elif command in ['load']:
            self.cmd_load()
        elif command in ['unload']:
            self.cmd_unload()
        elif command is None and alternatives is None:
            self.be.error("No command given.")
            self.print_help('usage')
        elif command is None and len(alternatives) > 0:
            self.be.error("Command '{c}' is ambiguous. See 'modm help'.".format(
                c=self.cmd))
            self.be.echo()
            self.be.echo("Did you mean one of these?")
            for a in alternatives:
                self.be.echo("  {u}[{t}]".format(
                    u=a[0:len(self.cmd)+1], t=a[len(self.cmd)+1:]))
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

    def parse_command(self, cmd):
        if cmd is None:
            return None, None
        commands = [c for c in self.available_commands if c.startswith(cmd)]
        if len(commands) == 1:
            command = commands[0]
            alternatives = []
        else:
            command = None
            alternatives = commands
        return command, alternatives

    def init_env(self):
        if not self.is_init_env:
            self.env = Env(modpath_var=self.modules_path_var,
                    modloaded_var=self.modules_loaded_var)
            self.is_init_env = True

    def init_modules(self):
        if not self.is_init_modules:
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
                        modversion = os.path.basename(modfile)
                        if modversion == self.module_default_file:
                            # Set default version
                            if self.modules[index].default is None:
                                defaultversion = ''
                                with open(modfile, 'r') as f:
                                    defaultversion = f.read().strip()
                                defaultversionfile = os.path.join(modpath,
                                        defaultversion)
                                if os.path.isfile(defaultversionfile):
                                    self.modules[index].default = (
                                            defaultversionfile)
                        elif modversion == self.module_help_file:
                            # Set help file
                            if self.modules[index].help_file is None:
                                self.modules[index].help_file = (
                                        os.path.join(modpath,
                                        self.module_help_file))
                        elif modversion == self.module_category_file:
                            # Set category
                            if self.modules[index].category is None:
                                with open(modfile, 'r') as f:
                                    self.modules[index].category = (
                                    f.read().strip())
                        else:
                            # Add version file
                            if modversion not in [
                                    os.path.basename(v)
                                    for v in self.modules[index].versions]:
                                self.modules[index].versions.append(modfile)
                            # Set loaded
                            if modfile in self.env.modloaded:
                                self.modules[index].loaded = modfile

            # Delete modules without versions (i.e. without module files)
            for i in range(len(self.modules)):
                if len(self.modules[i].versions) == 0:
                    del self.modules[i]
            # Sort modules
            self.modules = natsorted(self.modules,
                    key=lambda m: m.name)
            # Sort versions
            for i in range(len(self.modules)):
                self.modules[i].versions = natsorted(self.modules[i].versions,
                        key=lambda v: os.path.basename(v))
            # Set default modules for modules that do not have one
            for i in range(len(self.modules)):
                if self.modules[i].default is None:
                    self.modules[i].default = self.modules[i].versions[-1]
            # Set initialized state
            self.is_init_modules = True

    def init_parser(self):
        if not self.is_init_parser:
            self.parser = ModfileParser(self.env, self.be)

    def find_module(self, name, strict=False):
        modname, modversion = self.decode_name(name)
        for i, module in enumerate(self.modules):
            if module.name == modname:
                if strict and modversion is not None and (modversion not in
                        map(os.path.basename, module.versions)):
                    return None
                else:
                    return i
        return None

    def print_help(self, topic):
        help_file = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                Modm.help_file_dir, topic + Modm.help_file_suffix)

        if os.path.isfile(help_file):
            self.print_file(help_file)
        else:
            self.be.error("Help file '{f}' not found.".format(f=help_file),
                    internal=True)
            self.be.error("Please send an email with the command you used and "
                    + "the error message printed above to '{e}'."
                    .format(e=self.admin_email), internal=True)

    def print_file(self, path):
        with open(path, 'r') as f:
            self.be.echo(f.read(), newline=False)

    def cmd_help(self):
        topic = self.parse_command(self.args[0]) if len(self.args) > 0 else None
        if self.cmd in ['--help'] or topic is None:
            self.print_help('usage')
        elif topic in ['help']:
            self.print_help(os.path.join('commands', 'help'))
        elif topic in ['avail', 'status']:
            self.print_help(os.path.join('commands', 'avail'))
        elif topic in ['list']:
            self.print_help(os.path.join('commands', 'list'))
        elif topic in ['load']:
            self.print_help(os.path.join('commands', 'load'))
        elif topic in ['unload']:
            self.print_help(os.path.join('commands', 'unload'))
        else:
            self.init_modules()
            index = self.find_module(topic)
            if index is None:
                self.be.error("Unknown help topic '{t}'.".format(t=topic))
                self.be.error("See 'modm help help' for a list of help topics.")
            elif self.modules[index].help_file is None:
                self.be.error("No help available for module '{m}'.".format(
                    m=self.modules[index].name))
            else:
                self.print_file(self.modules[index].help_file)

    def cmd_version(self):
        self.be.echo("modm version {v}".format(v=__version__))

    def cmd_avail(self):
        self.init_env()
        self.init_modules()
        self.print_modules(self.modules)

    def print_modules(self, modules):
        maxlength = 0
        categories = set()
        # Determine all categories and the maximum length of the modules
        for module in modules:
            maxlength = max(maxlength, len(module.name))
            categories.add(module.category.strip().upper())
        # Natsort categories and put 'None' at the end if present
        if None in categories:
            categories = natsorted([c for c in categories if c is not None])
            categories.append(None)
        else:
            categories = natsorted(list(categories))
        # Print modules by category
        first = True
        for category in categories:
            if first:
                first = False
            else:
                self.be.echo('')
            self.be.echo(category if category else '<UNCATEGORIZED>')
            for module in [m for m in modules if
                    m.category.strip().upper() == category]:
                versions = []
                for version in module.versions:
                    v = os.path.basename(version)
                    if version == module.default:
                        v = v + '(default)'
                    if version in self.env.modloaded:
                        v = self.be.highlight(v + '*', kind='info')
                    versions.append(v)
                self.be.echo('  {m:{l}} {v}'.format(m=module.name+':', l=maxlength+1,
                        v=', '.join(versions)))

    def cmd_list(self):
        self.init_modules()
        for modfile in natsorted(self.env.modloaded):
            head, modversion = os.path.split(modfile)
            _, modname = os.path.split(head)
            self.be.echo(os.path.join(modname, modversion))

    def cmd_load(self):
        self.init_modules()
        self.init_parser()
        for name in self.args:
            index = self.find_module(name, strict=True)
            if index is not None:
                if self.is_loaded(name):
                    self.unload_module(self.decode_name(name)[0])
                self.load_module(name)
            else:
                self.be.error("Module '{m}' not found.".format(m=name))
        self.process_modified()
        self.be.export(self.env.modloaded_var, self.env.get_modloaded_str())

    def is_loaded(self, name):
        modname, _ = self.decode_name(name)
        if modname in [modname for modname, _ in
                map(self.decode_file, self.env.modloaded)]:
            return True
        else:
            return False


    def load_module(self, name):
        modfile = self.get_module_file(name)
        if modfile is None:
            return
        elif modfile in self.env.modloaded:
            return
        else:
            if self.parser.load(modfile):
                self.env.add_loaded_module(modfile)

    def unload_module(self, name):
        modname, modversion = self.decode_name(name)
        for modfile, (modnamefile, modversionfile) in zip(self.env.modloaded,
                map(self.decode_file, self.env.modloaded)):
            if modname == modnamefile and (
                    modversion is None or modversion == modversionfile):
                if self.parser.unload(modfile):
                    self.env.modloaded.remove(modfile)

    def get_module_file(self, name):
        i = self.find_module(name)
        if i is None:
            return None
        else:
            modname, modversion = self.decode_name(name)
            if not modversion:
                return self.modules[i].default
            else:
                modules = [modfile for modfile in self.modules[i].versions if
                    os.path.basename(modfile) == modversion]
                return modules[0] if len(modules) > 0 else None

    def decode_file(self, modfile):
        head, modversion = os.path.split(modfile)
        _, modname = os.path.split(head)
        return modname, modversion

    def decode_name(self, name):
        head, tail = os.path.split(name)
        modname = tail if head == '' else head
        modversion = tail if (head != '' and tail != '') else None
        return modname, modversion

    def cmd_unload(self):
        self.init_modules()
        self.init_parser()
        for name in self.args:
            self.unload_module(name)
        self.process_modified()
        self.be.export(self.env.modloaded_var, self.env.get_modloaded_str())

    def process_modified(self):
        for var in [var for var in self.env.variables.values()
                if var.is_modified()]:
            if var.is_unset():
                self.be.unset(var.get_name())
            else:
                self.be.export(*var.get_export())


# Run this script only if it is called directly
if __name__ == '__main__':
    main()
