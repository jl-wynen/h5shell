"""
Contains the shell and serves as main program to execute.
"""

import argparse
import shlex
import os.path

from commands import *
from h5manager import H5Manager

# import best available terminal backend
try:
    from vt100 import VT100 as Term
except ImportError:
    from terminal import Terminal as Term


def parse_args():
    """Parse command line arguments for h5sh."""
    parser = argparse.ArgumentParser(description="Interactive shell for HDF5 files.")
    parser.add_argument("FILE", help="HDF5 file to open")
    return parser.parse_args()


class H5sh:
    """
    The actual shell which glues all pieces together.
    """

    def __init__(self, term):
        self._term = term
        self._fname = ""
        self._wd = []

        # dict of available commands
        self._cmds = {
            "ls": ls.ls(),
            "cd": cd.cd(),
            "pwd": pwd.pwd()
        }

        # dict of aliases (evaluated before _cmds)
        self._aliases = {
            "..": "cd ..",
            "l": "ls -l"
        }

    def _build_prompt(self):
        """Build prompt for terminal."""

        prompt = ""

        # add file name and path
        filePath = os.path.split(self._fname)
        if filePath[0]:
            prompt += self._term.coloured(filePath[0]+"/", self._term.Colour.iblack)
        prompt += self._term.coloured(filePath[1], self._term.Colour.yellow)

        # add wd inside file
        prompt += "//"
        if self._wd:
            prompt += "/".join(self._wd[:-1] +
                               [self._term.coloured(self._wd[-1], self._term.Colour.iwhite)])
        prompt += " " + self._term.coloured("$", self._term.Colour.iyellow) + " "

        return prompt

    def run(self, fname):
        """
        Main REPL to run the shell.
        """

        self._fname = fname
        self._wd = []

        # 'open' the file
        mngr = H5Manager(fname)

        while True:
            inp = shlex.split(self._term.get_input(self._build_prompt()))

            # special treatment for exit
            if inp and inp[0].strip() == "exit":
                break

            try:
                # turn aliases into normal commands
                inp = shlex.split(self._aliases[inp[0]]) + inp[1:]
            except KeyError:
                pass

            try:
                # execute command
                self._cmds[inp[0]](inp[1:], self._wd, mngr, self._term)
            except KeyError:
                self._term.print("h5sh: {}: command not found".format(inp[0]))


if __name__ == "__main__":
    # run the shells REPL
    H5sh(Term()).run(parse_args().FILE)
