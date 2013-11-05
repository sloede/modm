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

* Linux or other Unix-like OS
* Python (>= 2.6)
* Bash (>= 4.1)


Installation
------------

Wait a minute! *Installation-free* it says up there! What the hell?

Well, the things you have to do are so minuscule, it is ridiculous. You only
need to change two files to adapt them to your needs:

### modm-init.sh
Set the correct path to your `modm.py` file and your default modules path. Users
can override the default path or add their own modules by *prepending* to the
path, just like it works with the Bash `PATH` variable.

### modm.py
You may set an admin email here (default: root@localhost). This email address
will only be displayed in case of internal errors, so that users know who to
report errors to.
