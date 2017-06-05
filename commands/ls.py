from . import command

class ls(command.Command):
    def __init__(self, term):
        super(ls, self).__init__(term)
        
        self._parser = command.Command.Parser(description="List information about the files (the current directory by default).")
        self._parser.add_argument("file", nargs="*", default=["."])
        self._parser.add_argument("-l", help="format as a list", action="store_true")
    
    def __call__(self, args, group):
        pa = self._parse_args(args)
        if not pa:
            return

        if pa.l:
            self._term.print("\n".join(group.keys()))
        else:
            self._term.print(" ".join(group.keys()))
