"""
Module for cd command.
"""

from . import command

from posixpath import normpath

from util import split_path, abspath

class cd(command.Command):
    """Command to change working directory."""

    def __init__(self):
        super(cd, self).__init__()

        self._parser = command.Command.Parser(description="Change the shell working directory.")
        self._parser.add_argument("group", nargs="?", default="/",
                                  help="HDF5 group to change to. The root of the file by default.")

    def __call__(self, args, wd, h5mngr, term):
        """Execute the cd command."""

        pa = self._parse_args(args, term)
        if not pa:
            return

        path = abspath(wd, [e for e in split_path(normpath(pa.group)) if e])
        if path:  # root is a group, only checky for other paths
            item = h5mngr.get_item(path)
            if not item:
                term.print("h5sh: cd: {}: No such dataset or group".format("/".join(path)))
                return
            if item.kind != item.Kind.group:
                term.print("h5sh: cd: {}: Not a group".format("/".join(path)))
                return

        # set the working path
        wd[:] = path
