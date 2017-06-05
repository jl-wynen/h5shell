from . import command

class cd(command.Command):
    def __init__(self, term):
        super(cd, self).__init__(term)
        
        self._parser = command.Command.Parser(description="Change the shell working directory (root by default).")
        self._parser.add_argument("dir", nargs="*", default=["/"])
    
    def __call__(self, args, group):
        pa = self._parse_args(args)
        if not pa:
            return

        # TODO
