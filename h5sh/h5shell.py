"""
Contains the shell.
"""

import argparse
import shlex
import os.path

from h5sh.commands import *
from h5sh.h5manager import H5Manager


# import best available terminal backend
try:
    from h5sh.vt100 import VT100 as Term
    TERM_KIND = "VT100"
except ImportError:
    from h5sh.terminal import Terminal as Term
    TERM_KIND = "FALLBACK"


VERSION = "1.0"


def parse_args():
    """Parse command line arguments for h5sh."""

    class VersionAction(argparse.Action):
        def __call__(self, parser, values, namespace, option_string):
            print("h5sh "+VERSION)
            parser.exit()

    parser = argparse.ArgumentParser(prog="h5sh",
                                     description="""
                                     Interactive shell for HDF5 files.
                                     h5sh tries to mimic the behaviour of
                                     common UNIX shells but supports only a subset of
                                     functionality. To see a list of available commands,
                                     type 'help' in a running shell.
                                     """,
                                     epilog="See https://github.com/jl-wynen/h5shell\
                                     for more information.")
    parser.add_argument("FILE", help="HDF5 file to open")
    parser.add_argument("--version", nargs=0, action=VersionAction,
                        help="Show the version number")
    return parser.parse_args()


class H5shell:
    """
    The actual shell which glues all pieces together.
    """

    def __init__(self):
        self._term = Term()
        self._wd = []

        # dict of available commands
        self._cmds = {
            "ls": ls.ls(),
            "cd": cd.cd(),
            "pwd": pwd.pwd(),
            "open": open_file.open_file(),
            "ext": run_external.run_external(),
            "history": history.history(),
        }

        # dict of aliases (evaluated before _cmds)
        self._aliases = {
            "..": "cd ..",
            "l": "ls -l",
            "-": "ext"
        }

        self._cmds["help"] = show_help.show_help(VERSION, self._cmds, self._aliases, TERM_KIND)

    def _build_prompt(self, h5mngr):
        """Build prompt for terminal."""

        prompt = ""

        # add file name and path
        filePath = os.path.split(h5mngr.get_file_name())
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

    def run(self):
        """
        Main REPL to run the shell.
        """

        self._wd = []

        # 'open' the file
        h5mngr = H5Manager(parse_args().FILE)

        while True:
            inp = shlex.split(self._term.get_input(self._build_prompt(h5mngr)))

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
                self._cmds[inp[0]](inp[1:], self._wd, h5mngr, self._term)
            except KeyError:
                self._term.print("h5sh: {}: command not found".format(inp[0]))
