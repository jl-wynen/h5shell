from . import command

from util import print_table, split_path, absolute_path

class ls(command.Command):
    def __init__(self):
        super(ls, self).__init__()
        
        self._parser = command.Command.Parser(description="List information about the files (the current directory by default).")
        self._parser.add_argument("file", nargs="*", default=["."])
        self._parser.add_argument("-l", help="format as a list", action="store_true")
    
    def __call__(self, args, wd, h5mngr, term):
        pa = self._parse_args(args, term)
        if not pa:
            return

        for f in pa.file:
            print("'"+f+"'")

            path = absolute_path(wd + split_path(f))

            try:
                items = h5mngr.list_contents(path)
            except KeyError:
                term.print("ls: cannot access '{}': No such dataset or group".format(f))
                return

            if items:
                if pa.l:
                    self._print_list(items, term)
                else:
                    self._print_plain(items, term)

    def _print_plain(self, items, term):
        print_table(list(items.keys()), term.get_width(), "  ", term.print)

    def _print_list(self, items, term):
        nameWidth = max(map(len, items.keys()))
        nameFmt = "{{:<{:d}}}".format(nameWidth)
        
        for name, item in items.items():
            if item.kind == item.Kind.dataset:
                term.print(nameFmt.format(name)+"      {"
                           +", ".join(str(x) for x in item.shape)+"} ("+str(item.dtype)+")")
            elif item.kind == item.Kind.group:
                term.print(nameFmt.format(name+"/"))
            elif item.kind == item.Kind.softLink:
                term.print(nameFmt.format(name)+"  ->  "+item.target)
            elif item.kind == item.Kind.externalLink:
                term.print(nameFmt.format(name)+"  ->  "+"//".join(item.target))
            elif item.kind == item.Kind.hardLink:
                raise NotImplemented
            
