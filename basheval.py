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
import textwrap

class BashEval:
    textwidth = 80
    replacements = {'$': '\$', '`': '\`', '\n': '\\n', '"': '\\"'}

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

    def wrap(self, message, width=None, keep_indent=True, dedent=False):
        if width is None:
            width = BashEval.textwidth

        if dedent:
            message = textwrap.dedent(message)

        final_newline = True if message and message[-1] == '\n' else False
        lines = []
        for line in message.splitlines():
            if keep_indent:
                indent = (len(line) - len(line.lstrip(' '))) * ' '
            else:
                indent = ''

            lines.append(
                    textwrap.fill(line, width=width, subsequent_indent=indent))

        return '\n'.join(lines) + ('\n' if final_newline else '')

    def quote(self, s):
        for pattern, substitute in BashEval.replacements.items():
            s = s.replace(pattern, substitute)
        return s

    def echo(self, message, kind='normal', newline=True, dedent=False):
        nl = r'\n' if newline else ''
        self.execute('printf "{m}{n}"'.format(
            m=self.highlight(self.quote(self.wrap(message, dedent=dedent)), kind=kind), n=nl))

    def error(self, message, newline=True, internal=False):
        prefix = "modm: Error: " if not internal else "modm: Error: "
        width = BashEval.textwidth - len(prefix)

        for line in self.wrap(message, width=width).splitlines():
            self.echo(prefix + line, kind='error', newline=newline)

    def export(self, key, value):
        self.execute("export {k}='{v}'".format(k=key, v=value))
