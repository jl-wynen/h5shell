"""
Module for pwd command.
"""

from . import command

class pwd(command.Command):
    """Command to current working directory."""

    def __init__(self):
        super(pwd, self).__init__()

        self._parser = command.Command.Parser(prog="pwd",
                                              description="Print the current working directory.")

    def __call__(self, args, wd, h5mngr, term):
        """Execute the pwd command."""

        if not self._parse_args(args, term):
            return

        term.print("/"+"/".join(wd))
