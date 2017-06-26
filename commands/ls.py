from . import command

from util import table_layout, split_path, absolute_path

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
        """Print table of H5 items."""
        
        # build layout using just the names
        separator = "   "
        widths = table_layout([len(s) for s in items], term.get_width(), len(separator))
        m = len(widths)

        # build new list containing the colour codes
        strs = []
        for name, item in items.items():
            if item.kind == item.Kind.group:
                strs.append(term.coloured(name, term.Colour.iblue)+"/")
            elif item.kind == item.Kind.softLink:
                strs.append(term.coloured(name, term.Colour.icyan)+"@")
            elif item.kind == item.Kind.externalLink:
                strs.append(term.coloured(name, term.Colour.cyan)+"@")
            else:
                strs.append(name)

        # print it
        for i in range(m):
            term.print(separator.join("{{:<{:d}}}".format(widths[i][j]).format(strs[j*m+i])
                                      for j in range(len(widths[i]))))

    def _print_list(self, items, term):
        """Print detailled list of H5 items, one item per row."""
        
        # make space for the name
        nameWidth = max(map(len, items.keys()))
        nameFmt = "{{:<{:d}}}".format(nameWidth)
        
        for name, item in items.items():
            if item.kind == item.Kind.dataset:
                term.print(nameFmt.format(name)+"      {"
                           +", ".join(str(x) for x in item.shape)+"} ("+str(item.dtype)+")")
            elif item.kind == item.Kind.group:
                term.print(nameFmt.format(term.coloured(name, term.Colour.iblue)+"/"))
            elif item.kind == item.Kind.softLink:
                term.print(term.coloured(nameFmt.format(name), term.Colour.icyan)
                           +"  ->  "+item.target)
            elif item.kind == item.Kind.externalLink:
                term.print(term.coloured(nameFmt.format(name), term.Colour.cyan)
                           +"  ->  "+term.coloured(item.target[0], term.Colour.iwhite)
                           +"//"+item.target[1])
            elif item.kind == item.Kind.hardLink:
                raise NotImplemented
            
