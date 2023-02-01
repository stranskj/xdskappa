# XDSkappa

[![DOI](https://zenodo.org/badge/499473647.svg)](https://zenodo.org/badge/latestdoi/499473647)

*XDSkappa* allows processing single crystal X-ray diffraction collected using multiaxis gonimeters with XDS. See `USAGE.md` for more details.

### Available jobs
List of the available jobs with short description is accessible using command `xdskappa`:
* xdskappa
* xdskappa.find
* xdskappa.optimize
* xdskappa.show_stat
* xdskappa.run_xds


## Requirements
The package requires Python 3.6 or newer. There are no extra modules needed for installation and usage. However, `setuptools_scm` is needed from package creation from Git source.

*XDSkappa* uses binaries from XDS package, which has to be installed separately, and uses different license. The XDS binaries (e.g. `xds_par` and `xscale_par`) have to be callable from the command line. Control files for *GNUplot* are generated for plotting various data processing statistics.

The package is heavily tested in Linux, it might work at macOS. 

## Installation
*XDSkappa* is standard Python package, therefore standard Python procedures can be used for installation. 

When Python3 is installed, recommended installation is using `pip`: 

```
pip3 install xdskappa-0.4.0-py3-none-any.whl
```

This is Python's packaging system, so also installs any potentially missing modules. *XDSkappa* will be installed for everybody, so you will probably need a root access (e.g. use `sudo`).


*Note:* `pip` is part of standard Python distribution, however, in some Linux distributions it might not be part of `python3` package; e.g. in Debian, you need also package `python3-pip`.

*Note 2:* In some systems, the `3`-suffix might not be needed. You can make sure of version being used by `python --version` or `pip --version`.

### Installation without root access

You can also install the package in userspace; e.g. you don't need root access, but nobody else in the system can use the package (unless they install it too):

```
pip3 install --user xdskappa-0.3.0.tar.gz
```

Now, *XDSkappa* is installed in `~/.local` folder. The run scripts (listed in *Available jobs*) are located in `~/.local/bin`, so we need to make it part of enviromental variable `PATH`. In `bash`:

```
export PATH=~/.local/bin:$PATH
```

You can put this command into your `~/.bashrc`, so it is applied automatically on log in.


### Custom path
The package can be also installed into a custom path. Unpack the archive:

```
tar xf atsas_mp-0.2.tar.gz
```

Now we need to set enviromental variables for installation. Assume, we are installing to `/my/path/xdskappa`. Include the path to PYTHONPATH enviromental variable:

```
export PYTHONPATH=/my/path/xdskappa:$PYTHONPATH
```

Then install *XDSkappa* using:

```
python setup.py install -d /my/path/xdskappa
```

At last, we need to set `PATH` to the run scripts:

```
export PATH=/my/path/xdskappa
```

Now, you might want to put earlier `PATH` and `PYTHONPATH` modifications in to your `~/.bashrc`, so it is loaded automatically on log in. Or you can handle it with Enviromental Modules (see below)


