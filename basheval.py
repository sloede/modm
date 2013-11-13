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
    """
    Class for converting commands, echos, variable definitions etc. to command
    strings for parsing by Bash's `eval` built-in function.
    """

    textwidth = 80
    replacements = {'$': '\$', '`': '\`', '\n': '\\n', '"': '\\"'}
    kinds = ['normal', 'info', 'success', 'error']

    def __init__(self, use_colors=True):
        """If `use_colors` is False, not colors are used for highlighting."""
        self.use_colors = use_colors
        self.cmds = []

    def clear(self):
        """Clear list of previously issued commands."""
        self.cmds = []

    def execute(self, cmd):
        """Add `cmd` to list of commands."""
        self.cmds.append(str(cmd))

    def cmdstring(self):
        """Get list of commands joined by ';' to be eval'd."""
        s = ';'.join(self.cmds)
        self.clear()
        return s

    def highlight(self, message, kind='normal'):
        """Add highlight to given `message`, depending on `kind`.

        `kind` may be 'normal', 'info', 'success', or 'error'. If `False` was
        passed to __init__ when building the object, no colors are added.
        """
        # Initialize kind to valid value
        if kind not in self.kinds:
            kind = 'normal'

        # Set prefix/suffix according to kind
        prefix = ''
        suffix = ''
        if not self.use_colors or kind == 'normal':
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
        """Wrap `message` to use it for nicely formatted program output.

        Arguments:
          message     -- text to wrap
          width       -- maximum line width (default: 80)
          keep_indent -- if true, keep indent of previous line when wrapping
          dedent      -- if true, remove common indent from all lines
        """
        # Init width if it was not set
        if width is None:
            width = BashEval.textwidth

        # Dedent common indentation
        if dedent:
            message = textwrap.dedent(message)

        # Store final newline as it will be lost in the later process
        final_newline = True if message and message[-1] == '\n' else False

        # Split lines and wrap them individually
        lines = []
        for line in message.splitlines():
            # Calculate indent for subsequent lines
            if keep_indent:
                indent = (len(line) - len(line.lstrip(' '))) * ' '
            else:
                indent = ''

            # Do the wrapping
            lines.append(textwrap.fill(line, width=width,
                                       subsequent_indent=indent,
                                       drop_whitespace=False))

        # Join the lines and add final newline if it was originally present
        return '\n'.join(lines) + ('\n' if final_newline else '')

    def quote(self, s):
        """Quote string for usage in Bash double-quotes."""
        for pattern, substitute in BashEval.replacements.items():
            s = s.replace(pattern, substitute)
        return s

    def echo(self, message='', kind='normal', newline=True, dedent=False):
        """Generate command to print `message` using 'printf'.

        Arguments:
          message -- message to print
          kind    -- type of highlighting to apply (cf. `highlight()`)
          newline -- if true, add newline to message
          dedent  -- if true, remove common indent from all lines (cf. `wrap()`)
        """
        # Add newline only if option is set
        nl = r'\n' if newline else ''

        # Add printf command to command queue
        self.execute('printf "{m}{n}"'.format(m=self.highlight(self.quote(
                self.wrap(message, dedent=dedent)), kind=kind), n=nl))

    def error(self, message, newline=True, internal=False):
        """Generate command to print error message.

        Arguments:
          message  -- error message to print
          newline  -- if true, add newline to message
          internal -- if true, apply additional formatting for internal errors
        """
        # Set prefix depending on whether this is an internal error
        prefix = "modm: Error: " if not internal else "modm: Internal error: "

        # Get correct width for wrapping
        width = BashEval.textwidth - len(prefix)

        # Wrap message and prefix each line before printing an error
        for line in self.wrap(message, width=width).splitlines():
            self.echo(prefix + line, kind='error', newline=newline)

    def export(self, key, value):
        """Set environment variable `key` to `value` and export it."""
        self.execute("export {k}='{v}'".format(k=key, v=value))

    def unset(self, key):
        """Unset environment variable `key`."""
        self.execute("unset {k}".format(k=key))
