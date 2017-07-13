"""
Module for history command.
"""

from . import command

class history(command.Command):
    """Command to show input history."""

    def __init__(self):
        super(history, self).__init__()

        self._parser = command.Command.Parser(prog="history",
                                              description="Show the input history")

    def __call__(self, args, wd, h5mngr, term):
        """Execute the history command."""

        if not self._parse_args(args, term):
            return

        term.print(term.history.dump())
