"""
Module for show_help command.
"""

from . import command

class show_help(command.Command):
    """Command to display help message."""

    def __init__(self, version, cmds, aliases, termKind):
        super(show_help, self).__init__()

        self._parser = command.Command.Parser(description="Show a help message.")

        self._version = version
        self._cmds = cmds
        self._aliases = aliases
        self._termKind = termKind

    def __call__(self, args, wd, h5mngr, term):
        """Execute the help command."""


        helpStr = \
"""\
h5sh version {version}

Currently opened file: '{fname}'

Available commands:
         exit  =  Exit the shell
   {commands}

Aliases:
   {aliases}

Use option --help on a command to see a description.
""".format(version=self._version, fname=h5mngr.get_file_name(),
           commands="\n   ".join("{:>10s}  =  {}".format(cmd, self._cmds[cmd]\
                                                         .get_description().split(".")[0])
                                 for cmd in self._cmds),
           aliases="\n   ".join("{:>10s}  =  '{}'".format(ali, val)
                                for ali, val in self._aliases.items()))

        if self._termKind == "VT100":
            helpStr += \
"""
The terminal backend is VT100; advanced input is supported.
"""
        else:
            helpStr += \
"""
The terminal backend is fallback; only basic input is available.
"""

        helpStr += \
"""
For more information visit https://github.com/jl-wynen/h5shell\
"""

        term.print(helpStr)
