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
    """If this file is run as a script, `main()` will be executed.

    Creates `Modm` instance and calls `run()` on it.
    """
    Modm(sys.argv).run()

class Modm:
    """
    Class to manage modules.

    Supports loading, unloading and listing of modules. Provides built-in help.
    """

    help_file_suffix = '.txt'
    help_file_dir = 'doc'
    module_help_file = '.help'
    module_default_file = '.default'
    module_category_file = '.category'
    modules_path_var = 'MODM_MODULES_PATH'
    modules_loaded_var = 'MODM_LOADED_MODULES'
    admin_email_var = 'MODM_ADMIN_EMAIL'
    color_setting_var = 'MODM_USE_COLORS'
    admin_default_email = 'root@localhost'
    available_commands = ['avail', 'status', 'help', 'list', 'load', 'unload']

    def __init__(self, argv=['modm.py']):
        """Save arguments and initialize member variables.

        Arguments:
          argv -- should be called with `sys.argv`, otherwise a list with at
                  least one item has to be provided
        """
        # Save arguments
        self.argv = argv

        # Disable use of colors if environment variable is set to 'off' value
        if self.color_setting_var in os.environ and (
                os.environ[self.color_setting_var].lower() in
                ['no', 'off', 'false']):
            use_colors = False
        else:
            use_colors = True

        # Create Bash evaluation instance
        self.be = BashEval(use_colors)

        # Set admin email address to environment variable if found, otherwise
        # to built-in default
        if self.admin_email_var in os.environ:
            self.admin_email = os.environ[self.admin_email_var]
        else:
            self.admin_email = self.admin_default_email

        # Init other members
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
        """Call `runsafe()` in try-except block to catch irregular errors and
        print command string from BashEval."""
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
        """Parse command line arguments and execute specified command."""
        # Init command line arguments
        self.init_argv()

        # Parse command for alternatives
        command, alternatives = self.parse_command(self.cmd)

        # Check command and execute appropriate method
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
            # If no command was given, show usage information
            self.be.error("No command given.")
            self.print_help('usage')
        elif command is None and len(alternatives) > 0:
            # If partial command was specified but is ambiguous, show list of
            # valid possibilities
            self.be.error("Command '{c}' is ambiguous. See 'modm help'.".format(
                    c=self.cmd))
            self.be.echo()
            self.be.echo("Did you mean one of these?")
            for a in alternatives:
                self.be.echo("  {u}[{t}]".format(
                        u=a[0:len(self.cmd)+1], t=a[len(self.cmd)+1:]))
        else:
            arg_type = "Option" if self.cmd[0] == '-' else "Command"
            self.be.error("{t} '{c}' not recognized.".format(
                    t=arg_type, c=self.cmd))
            self.print_help('usage')

    def init_argv(self):
        """Initialize command line arguments if not yet done."""
        if not self.is_init_argv:
            # Command is set to None if none was found
            self.cmd = self.argv[1] if len(self.argv) > 1 else None

            # Arguments are set to empty list if none were found
            self.args = self.argv[2:] if len(self.argv) > 2 else []
            self.is_init_argv = True

    def init_env(self):
        """Initialize environment handler if not yet done."""
        if not self.is_init_env:
            self.env = Env(modpath_var=self.modules_path_var,
                           modloaded_var=self.modules_loaded_var)
            self.is_init_env = True

    def init_modules(self):
        """Initialize all modules if not yet done.

        Check all module paths for all available modules and their versions,
        defaults, categories etc. For a module with a given name, the first
        module found in the modules path overrides the settings for all later
        modules. However, it is possible that later versions are appended.
        """
        # Only initialize if not yet done
        if not self.is_init_modules:
            self.init_env()

            # Iterate over directories containing the modules
            for modules_directory in self.env.modpath:
                # Iterate over module folders
                for name in [d for d in os.listdir(modules_directory) if
                        os.path.isdir(os.path.join(modules_directory, d))]:
                    # Get module index (if existing)
                    index = self.find_module(name)

                    # If module does not yet exist, create a new one
                    if index == None:
                        self.modules.append(Module())
                        index = len(self.modules) - 1

                    # Set module name if not yet set
                    if self.modules[index].name is None:
                        self.modules[index].name = name

                    # Set module versions
                    modpath = os.path.join(modules_directory, name)
                    for modfile in [os.path.join(modpath, f) for f in
                            os.listdir(modpath) if
                            os.path.isfile(os.path.join(modpath, f))]:
                        _, modversion = self.decode_file(modfile)

                        # Check if filename matches any of the special names
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
            self.modules = natsorted(self.modules, key=lambda m: m.name)

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
        """Initialize module filer parser if not yet done."""
        if not self.is_init_parser:
            self.parser = ModfileParser(self.env, self.be)

    def find_module(self, name, strict=False):
        """Return the index of a module with name `name`.

        If no module was found with this name, return None. By default only the
        module name is checked, however, if `name` contains a version number and
        `strict` is set to true, also the version is checked for existence.
        """
        # Get name, version
        modname, modversion = self.decode_name(name)

        # Check all modules for the name (and possibly version)
        for i, module in enumerate(self.modules):
            if module.name == modname:
                if strict and modversion is not None and (modversion not in
                        map(os.path.basename, module.versions)):
                    return None
                else:
                    return i
        return None

    def get_module_file(self, name):
        """Get a module file from the name. If no version is specified, return
        default module.
        """
        # Get module index
        i = self.find_module(name)
        if i is None:
            return None
        else:
            # If module was found, decode name
            modname, modversion = self.decode_name(name)

            # Return default if no module version was found
            if not modversion:
                return self.modules[i].default
            # Otherwise return module file
            else:
                modules = [modfile for modfile in self.modules[i].versions if
                        os.path.basename(modfile) == modversion]
                return modules[0] if len(modules) > 0 else None

    def decode_file(self, modfile):
        """Split a module file path into its module name and version
        components.
        """
        head, modversion = os.path.split(modfile)
        _, modname = os.path.split(head)
        return modname, modversion

    def decode_name(self, name):
        """Split a module name into its module name and version components."""
        head, tail = os.path.split(name)
        modname = tail if head == '' else head
        modversion = tail if (head != '' and tail != '') else None
        return modname, modversion

    def parse_command(self, cmd):
        """Parse (partial) command for known commands. Return tuple of full
        command name and a list of alternatives if ambiguous.
        """
        # Return None if no command was specified
        if cmd is None:
            return None, None

        # Get list of matching commands
        commands = [c for c in self.available_commands if c.startswith(cmd)]

        # If only one command matches, this is it: list of alternatives is empty
        if len(commands) == 1:
            command = commands[0]
            alternatives = []
        # Otherwise return no command but only the alternatives
        else:
            command = None
            alternatives = commands

        # Return tuple
        return command, alternatives

    def print_file(self, path):
        """Open file at `path` and print its contents using BashEval."""
        with open(path, 'r') as f:
            self.be.echo(f.read(), newline=False)

    def print_help(self, topic):
        """Print help file associated with `topic`. Issues error message if
        topic was not found."""
        # Get help file path as combination of modm.py file path and topic
        # plus help file extension
        help_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 Modm.help_file_dir,
                                 topic + Modm.help_file_suffix)

        # If file exists, print its contents
        if os.path.isfile(help_file):
            self.print_file(help_file)
        # Otherwise print error message. Since this should never happen, it is
        # an internal error
        else:
            self.be.error("Help file '{f}' not found.".format(f=help_file),
                          internal=True)
            self.be.error("Please send an email with the command you used and "
                          + "the error message printed above to '{e}'.".format(
                          e=self.admin_email), internal=True)

    def print_modules(self, modules):
        """All modules in list `modules`, sorted by category."""
        # Determine all categories and the maximum length of the modules
        maxlength = 0
        categories = set()
        for module in modules:
            maxlength = max(maxlength, len(module.name))
            categories.add(module.category.strip().upper()
                           if module.category else None)

        # Natsort categories and put 'None' at the end if present
        if None in categories:
            categories = natsorted([c for c in categories if c is not None])
            categories.append(None)
        else:
            categories = natsorted(list(categories))

        # Print modules by category
        first = True
        for category in categories:
            # For the first category, no newline is needed
            if first:
                first = False
            else:
                self.be.echo('')

            # Print category name
            self.be.echo(category if category else '<UNCATEGORIZED>')

            # Print each module in category
            for module in [m for m in modules if (
                    (True if category is None else False) if (
                        m.category is None) else (
                    m.category.strip().upper() == category))]:

                # Get all versions of module
                versions = []
                for version in module.versions:
                    v = os.path.basename(version)
                    if version == module.default:
                        v = v + '(default)'
                    if version in self.env.modloaded:
                        v = self.be.highlight(v + '*', kind='info')
                    versions.append(v)

                # Print module together with all its version, in which
                # the default version and the currently loaded version are
                # marked specially
                self.be.echo('  {m:{l}} {v}'.format(m=module.name+':',
                             l=maxlength+1, v=', '.join(versions)))

    def is_loaded(self, name):
        """Return True if module `name` is loaded, else False."""
        modname, _ = self.decode_name(name)
        if modname in [modname for modname, _ in
                map(self.decode_file, self.env.modloaded)]:
            return True
        else:
            return False


    def load_module(self, name):
        """Load module `name` if it is not yet loaded."""
        # Get full path to module file
        modfile = self.get_module_file(name)

        # If module file was not found, return
        if modfile is None:
            return
        # Otherwise, if module is already loaded, return
        elif modfile in self.env.modloaded:
            return
        # Otherwise, parse module file for loading and add module to list of
        # loaded modules
        else:
            if self.parser.load(modfile):
                self.env.add_loaded_module(modfile)

    def unload_module(self, name):
        """Unload module `name` if it is currently loaded."""
        # Get module name and version
        modname, modversion = self.decode_name(name)

        # Get module file, name, and version from currently loaded modules
        for modfile, (modnamefile, modversionfile) in zip(
                self.env.modloaded,
                map(self.decode_file, self.env.modloaded)):
            # If module name matches, unload module and remove module from
            # list of loaded modules
            if modname == modnamefile and (
                    modversion is None or modversion == modversionfile):
                if self.parser.unload(modfile):
                    self.env.modloaded.remove(modfile)

    def process_modified(self):
        """Check all modified environment variables and unset/export them as
        needed.
        """
        # Iterate over all variables that were modified
        for var in [var for var in self.env.variables.values()
                if var.is_modified()]:
            # Unset variable if it is marked for unset
            if var.is_unset():
                self.be.unset(var.get_name())
            # Otherwise update its value
            else:
                self.be.export(*var.get_export())

    def cmd_avail(self):
        """Command 'avail': list all available modules by category."""
        self.init_env()
        self.init_modules()
        self.print_modules(self.modules)

    def cmd_help(self):
        """Command 'help': show help on commands or modules."""
        # Get help topic from arguments and parse for commands
        topic = self.args[0] if len(self.args) > 0 else None
        command, alternatives = self.parse_command(topic)

        # If no topic was specified, show usage information
        if self.cmd in ['--help'] or topic is None:
            self.print_help('usage')
        # If a command was specified, print its help file
        elif command in ['help']:
            self.print_help(os.path.join('commands', 'help'))
        elif command in ['avail', 'status']:
            self.print_help(os.path.join('commands', 'avail'))
        elif command in ['list']:
            self.print_help(os.path.join('commands', 'list'))
        elif command in ['load']:
            self.print_help(os.path.join('commands', 'load'))
        elif command in ['unload']:
            self.print_help(os.path.join('commands', 'unload'))
        # If no command was determined but there are alternatives, show a list
        # of ambiguous commands
        elif command is None and len(alternatives) > 0:
            self.be.error("Command '{c}' is ambiguous. See 'modm help'.".format(
                          c=topic))
            self.be.echo()
            self.be.echo("Did you mean one of these?")
            for a in alternatives:
                self.be.echo("  {u}[{t}]".format(
                    u=a[0:len(self.cmd)+1], t=a[len(self.cmd)+1:]))
        # Otherwise, check modules for help
        else:
            self.init_modules()
            index = self.find_module(topic)

            # If no module was found with the name `topic`, show error
            if index is None:
                self.be.error("Unknown help topic '{t}'.".format(t=topic))
                self.be.error("See 'modm help help' for a list of help topics.")
            # Otherwise show error if no help file was set for the module
            elif self.modules[index].help_file is None:
                self.be.error("No help available for module '{m}'.".format(
                    m=self.modules[index].name))
            # Otherwise (help file was found for module), print help file
            else:
                self.print_file(self.modules[index].help_file)

    def cmd_list(self):
        """Command 'list': show all currently loaded modules."""
        self.init_modules()

        # Print all loaded modules in an easily parsable list
        for modfile in natsorted(self.env.modloaded):
            head, modversion = os.path.split(modfile)
            _, modname = os.path.split(head)
            self.be.echo(os.path.join(modname, modversion))

    def cmd_load(self):
        """Command 'load': load all specified module files."""
        self.init_modules()
        self.init_parser()

        # Try to load each argument as a module
        for name in self.args:
            index = self.find_module(name, strict=True)
            # If module was found, load it
            if index is not None:
                # If a version of the module is currently loaded, unload it
                if self.is_loaded(name):
                    self.unload_module(self.decode_name(name)[0])
                self.load_module(name)
            # Otherwise print error
            else:
                self.be.error("Module '{m}' not found.".format(m=name))

        # After loading all modules, act on all environment variables that
        # have changed
        self.process_modified()
        self.be.export(self.env.modloaded_var, self.env.get_modloaded_str())

    def cmd_unload(self):
        """Command 'unload': unload all specified module files."""
        self.init_modules()
        self.init_parser()

        # Unload each argument
        for name in self.args:
            self.unload_module(name)

        # After unloadig all modules, act on all environment variables that
        # have changed
        self.process_modified()
        self.be.export(self.env.modloaded_var, self.env.get_modloaded_str())

    def cmd_version(self):
        """Print version information."""
        self.be.echo("modm version {v}".format(v=__version__))


# Run this script only if it is called directly
if __name__ == '__main__':
    main()
