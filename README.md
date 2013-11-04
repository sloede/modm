Modm - Modules iMproved
=======================

This package aims to mimic some of the functionality provided by the Tcl
`modules` program, which can be used to set up a shell environment as desired.
So called *module files* contain information on e.g. `PATH` or `LD_LIBRARY_PATH`
settings and modify these environment variables accordingly.

Although the name implies that this program can do everything that the original
`modules` can but better, this is not exactly true. The main goal is to provide
*some* functions of the original `modules`, but without the hassle of installing
`Tcl` or `modules` itself,  or handling `Tcl` code.


Features
--------

* Completely written in Python
* Installation-free
* Nothing else :(

Planned (intermediate future):

* Set `PATH` and `LD_LIBRARY_PATH` variables
* Nicely formatted and *colorized* output


Planned (in a land far, far away):

* Support other shells than `bash`
* Support a richer modulefile syntax


Requirements
------------

* Python (>= 2.6)
* Bash (>= 4.1)
