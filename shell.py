import shlex
from h5manager import H5Manager

from commands import *
            

class Shell:
    def __init__(self, term):
        self._term = term

        self._cmds = {
            "ls": ls.ls()
        }

    def _set_prompt(self):
        self._term.prompt = "{file}//{wd} $ ".format(file=self._fname, wd="/".join(self._wd))

    def change_directory(self, d):
        # TODO
        pass
        
    def run(self, fname):
        self._fname = fname
        self._wd = []

        mngr = H5Manager(fname)

        while True:
            self._set_prompt()
            inp = shlex.split(self._term.get_input())
            
            if inp and inp[0].strip() == "exit":
                break
            
            try:
                self._cmds[inp[0]](inp[1:], self._wd, mngr, self._term)
            except KeyError:
                self._term.print("h5shell: {}: command not found".format(inp[0]))

