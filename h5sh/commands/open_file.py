"""
Module for open_file command.
"""

import re

from . import command

class open_file(command.Command):
    """Command to open a new HDF5 file."""

    def __init__(self):
        super(open_file, self).__init__()

        self._parser = command.Command.Parser(prog="open",
                                              description="Switch to another HDF5 file.")
        self._parser.add_argument("file",
                                  help="File to open. Path is relative to the directory from which you launched h5sh.")

    def __call__(self, args, wd, h5mngr, term):
        """Execute the open_file command."""

        pa = self._parse_args(args, term)
        if not pa:
            return

        try:
            h5mngr.read_file(pa.file)
        except OSError as error:
            # dig out the reason from error and show it
            term.print("Could not open file '{}': {}" \
                       .format(pa.file,
                               re.match(".*error message = ([^,]+),",
                                        error.args[0]).group(1)))
