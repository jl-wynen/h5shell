import shlex
import os.path

from commands import *
from h5manager import H5Manager

class Shell:
    def __init__(self, term):
        self._term = term
        self._fname = ""
        self._wd = []

        self._cmds = {
            "ls": ls.ls(),
            "cd": cd.cd(),
            "pwd": pwd.pwd()
        }

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

