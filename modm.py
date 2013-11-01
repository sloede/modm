#!/usr/bin/env python2

# Set directory with module files
modules_dir = '/home/mic/Code/aiamodule/modules'

import os
import sys

def main():
    # Parse arguments
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'help'
    args = sys.argv[2:] if len(sys.argv) > 2 else []

    be = BashExec()
    commands_available = ['avail', 'help', 'list', 'load', 'unload']
    if cmd not in commands_available:
        be.echo("normal message")
        be.echo("info message", 'info')
        be.echo("success message", 'success')
        be.echo("error message", 'error')
        be.echo("bad kind,no newline", 'bad', False)
        be.echo("        normal")
        be.error("real error")
        print be.cmdstring()
        return

class Modm:
    def __init__(self, *modules_dirs):
        self.modules_dirs = modules_dirs
        self.cmd = None
        self.args = []
        self.be = BashExec()
        self.categories = []
        self.mod_available = []
        self.mod_loaded = []

    def run(self):
        self.parseargs()

class BashExec:
    def __init__(self):
        self.cmds = []

    def execute(self, cmd):
        self.cmds.append(str(cmd))

    def cmdstring(self):
        return ';'.join(self.cmds)

    def echo(self, message, kind='normal', newline=True):
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
        nl = r'\n' if newline else ''
        self.execute('printf "{p}{m}{s}{n}"'.format(
                p=prefix, m=message, s=suffix, n=nl))

    def error(self, message, newline=True):
        self.echo("*** ERROR: " + message, kind='error', newline=newline)

    def export(self, key, value):
        self.execute("export {k}={v}".format(k=key, v=value))



# Run this script only if it is called directly
if __name__ == '__main__':
    main()
