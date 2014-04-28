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


# Note: The code in this file was inspired by a comment on the following site:
#       http://nedbatchelder.com/blog/200712/human_sorting.html#comments

import re

def natsorted(l, **args):
    """Sort the given iterable in a way that humans expect."""
    # Define method to convert items to integers
    convert = lambda s: int(s) if s.isdigit() else s

    # Return None if 'cmp' is set since it is not supported
    if 'cmp' in args:
        return None

    # Define lambda `keyfun` to translate values if a `key` argument
    # was specified
    if 'key' in args:
        keyfun = args['key']
        del args['key']
    else:
        keyfun = lambda x: x

    # Define lambda to get alphanumeric key
    alphanum_key = lambda key: [convert(c) for c in
            re.split('([0-9]+)', keyfun(key))]

    # Return new list that is sorted naturally, while passing on all
    # other arguments to `sorted()`
    return sorted(l, key=alphanum_key, **args)
