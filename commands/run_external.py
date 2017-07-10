"""
Module for run_external command.
"""

import subprocess
import argparse

from . import command

class run_external(command.Command):
    """Command to run an external command."""

    def __init__(self):
        super(run_external, self).__init__()

        self._parser = command.Command.Parser(
            description="Execute commands in the system shell.\
            The working directory is the directory you launched h5sh from.")
        self._parser.add_argument("cmd", nargs=argparse.REMAINDER,
                                  help="Command(s) to execute.")

    def __call__(self, args, wd, h5mngr, term):
        """Execute the run_external command."""

        pa = self._parse_args(args, term)
        if not pa:
            return

        try:
            proc = subprocess.run(pa.cmd)

            if proc.returncode != 0:
                term.print("Command exited with nonzero return code: {}.".format(proc.returncode))

        except FileNotFoundError:
            term.print("Command '{}' could not be found".format(pa.cmd[0]))
