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

*   Completely written in Python
*   Installation-free
*   Built-in documentation for commands
*   Partial commands
*   Module file syntax:
    *   Append/prepend environment variables of path and string type
    *   Set environment variables while preserving previous values
    *   Print messages on loading/unloading
*   Nicely formatted and *colorized* output
*   Modules organized by categories
*   Built-in documentation for modules

Planned (in a land far, far away):

*   Support other shells than `bash`
*   Support a richer modulefile syntax


Requirements
------------

*   Python (>= 2.6)
*   Bash (>= 4.1)
*   any Unix-like OS that
    * uses `\n` as the newline separator


Getting Modm
------------

In order to obtain Modm, just clone the repository into a directory of your
choice, e.g.

    git clone https://github.com/sloede/modm.git path/to/modm

This will get you the latest and coolest version of Modm. Note that the current
git `HEAD` might contain experimental changes that will disappear later on, also
the repository `HEAD` might have the odd unresolved bug in it (although I try
not to push to GitHub if there is still something wrong).

If you need to be sure that the Modm version you get is stable, check out the
latest tagged version of Modm. The repository is tagged from time to time when
a stable version of Modm has been reached, thus the tagged commits should be
error-free.

If you want the latest stable version, list all available tags using

    git tag

in your cloned repository. Then scroll down for the highest version number (e.g.
*v1.0*) and check it out with

   git checkout tags/v1.0

Alternatively, have a look at the *Releases* tab on the GitHub website:
[https://github.com/sloede/modm](https://github.com/sloede/modm)


Installation
------------

Wait a minute! *Installation-free* it says up there! What the hell?

Well, the things you have to do are so minuscule, it is ridiculous. You only
need to edit one file to adapt Modm to your needs:

### modm-init.sh
Set the correct path to your `modm.py` file and your default modules path. Users
can override the default path or add their own modules by *prepending* to the
path, just like it works with the Bash `PATH` variable. You can also set an
admin email variable so that users know who to ask if they encounter internal
errors (oops...).

You need to do this only once per installation.

### .bashrc/.bash\_profile/.profile
In one of the Bash configuration files that are sourced at startup/login,
`modm-init.sh` must be sourced, i.e. like so:

    source path/to/modm/installation/modm-init.sh

This makes the `modm` command available in the shell.

You need to do this for each users that wishes to use `modm`. Alternatively, if
you have access to it, you could also put this in `/etc/profile` so that it is
sourced for all users. And don't worry - sourcing `modm-init.sh` multiple times
does not create any problems.


Usage
-----

After installation, make sure that the `modm-init.sh` is sourced properly, e.g.
by logging out and in again. Then just execute `modm` in the shell and let the
built-in documentation take it from there.

*Note:* You may disable colorized output by setting the environment variable
`MODM_USE_COLORS` to `off`.
