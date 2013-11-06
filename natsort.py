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


# Note: The code in this file was inspired by a comment on the following site:
#       http://nedbatchelder.com/blog/200712/human_sorting.html#comments

import re

def natsorted(l, **args):
    """Sort the given iterable in a way that humans expect."""
    convert = lambda s: int(s) if s.isdigit() else s
    if args.has_key('cmp'):
        return None
    if args.has_key('key'):
        keyfun = args['key']
        del args['key']
    else:
        keyfun = lambda x: x
    alphanum_key = lambda key: [convert(c) for c in
            re.split('([0-9]+)', keyfun(key))]
    return sorted(l, key=alphanum_key, **args)
