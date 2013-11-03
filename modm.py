#!/usr/bin/env python

# Set name of environment variable with locations of modules
modules_path_var = 'MODM_MODULES_PATH'

# Set name of environment variable with names of loaded modules
modules_loaded_var = 'MODM_LOADED_MODULES'

# Set email address to show in error messages
admin_email = 'root@localhost'

import os
import sys
import textwrap as tw

def main():
    m = Modm(sys.argv, modules_path_var, modules_loaded_var, admin_email)
    m.run()

class Modm:
    def __init__(self, argv, modules_path_var='MODM_MODULES_PATH',
            modules_loaded_var='MODM_LOADED_MODULES',
            admin_email='root@localhost'):
        self.argv = argv
        self.modules_path_var = modules_path_var
        self.modules_loaded_var = modules_loaded_var
        self.admin_email = admin_email
        self.cmd = None
        self.args = []
        self.be = BashEval()

    def run(self):
        try:
            self.rununsafe()
        except Exception as e:
            self.be.clear()
            self.be.error("An unknown error has occurred.")
            self.be.error("Please send an email with the used command and "
                    + "the error message above to '{e}'."
                    .format(e=self.admin_email))
            raise
        finally:
            print self.be.cmdstring()

    def rununsafe(self):
        self.init_argv()

        if self.cmd in ['help', '-h', '--help']:
            self.cmd_help()
        elif self.cmd in ['avail']:
            self.cmd_avail()
        elif self.cmd in ['list', 'loaded']:
            self.cmd_list()
        elif self.cmd in ['load']:
            self.cmd_load()
        elif self.cmd in ['unload']:
            self.cmd_unload()
        elif not self.cmd:
            self.be.error("No command given." +
                    "See 'modm help' for usage information.")
        else:
            self.be.error("Command '{c}' not recognized. ".format(c=self.cmd) +
                    "See 'modm help' for usage information.")

    def init_argv(self):
        self.cmd = self.argv[1] if len(self.argv) > 1 else None
        self.args = self.argv[2:] if len(self.argv) > 2 else []

class Env:
    exepath_var = 'PATH'
    libpath_var = 'LD_LIBRARY_PATH'
    path_sep = ':'

    def __init__(self):
        # Load PATH to exepath
        self.exepath = (os.environ[self.exepath_var].split(self.path_sep) if
        os.environ.has_key(exepath_var) else [])
        if self.exepath == ['']:
            self.exepath = []

        # Load LD_LIBRARY_PATH to libpath
        self.libpath = (os.environ[self.libpath_var].split(self.path_sep) if
        os.environ.has_key(libpath_var) else [])
        if self.libpath == ['']:
            self.libpath = []

    def get_exepath_str(self):
        return Env.path_sep.join(self.exepath)

    def get_libpath_str(self):
        return Env.path_sep.join(self.libpath)

class BashEval:
    textwidth = 80

    def __init__(self):
        self.cmds = []

    def clear(self):
        self.cmds = []

    def execute(self, cmd):
        self.cmds.append(str(cmd))

    def cmdstring(self):
        string = ';'.join(self.cmds)
        self.clear()
        return string

    def highlight(self, message, kind='normal'):
        kinds = ['normal', 'info', 'success', 'error']
        if kind not in kinds:
            kind = 'normal'
        prefix = ''
        suffix = ''
        if kind == 'normal':
            pass
        elif kind == 'info':
            prefix = r'\033[34m'
            suffix = r'\033[0m'
        elif kind == 'success':
            prefix = r'\033[32m'
            suffix = r'\033[0m'
        elif kind == 'error':
            prefix = r'\033[31m'
            suffix = r'\033[0m'

        return '{p}{m}{s}'.format(p=prefix, m=message, s=suffix)

    def reformat(self, message, width=None, keep_indent=True):
        if width is None:
            width = BashEval.textwidth

        lines = []
        for line in message.splitlines():
            if keep_indent:
                indent = (len(line) - len(line.lstrip(' '))) * ' '
            else:
                indent = ''

            lines.append(tw.fill(line, width=width, subsequent_indent=indent))

        return ''.join(lines)

    def echo(self, message, kind='normal', newline=True):
        nl = r'\n' if newline else ''
        self.execute('printf "{m}{n}"'.format(
                m=self.highlight(message, kind=kind), n=nl))

    def error(self, message, newline=True):
        self.echo("*** ERROR: " + message, kind='error', newline=newline)

    def export(self, key, value):
        self.execute("export {k}={v}".format(k=key, v=value))



# Run this script only if it is called directly
if __name__ == '__main__':
    main()
