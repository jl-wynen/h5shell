h5shell
=======
An interactive shell to browse HDF5 files.

This shell allows to navigate `HDF5 <https://support.hdfgroup.org/HDF5/>`_ files
interactively and behaves similarly to common UNIX shells like
``sh`` or ``bash``. Currently, the following commands are supported:
``exit, ls, cd, pwd, help``.

Requirements
------------
Necessary
+++++++++
- Python3 (tested with version 3.6.1)
- `h5py <http://www.h5py.org/>`_
  
Optional
++++++++
- Python packages ``termios`` and ``tty`` for advanced input and output.
  They are usually preinstalled if your system supports them.
- `psutil <https://pypi.python.org/pypi/psutil>`_;
  only needed to allow suspending the shell if the above packages are used.
- `sphinx_rtd_theme <https://github.com/rtfd/sphinx_rtd_theme>`_ for documentation.

Usage
-----
Currently, there is no install script. Just run `python h5sh.py FILE` to launch the shell. A proper way to install it will be added in the future.
