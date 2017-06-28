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
            # TODO detect groups and print their name iff there is more than one file parameter
            # print("'"+f+"'")

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

        nameStrs, nameLens, _ = self._compile_data(items, term)
        
        # build layout w/o respecting colour codes
        separator = "   "
        widths = table_layout(nameLens, term.get_width(), len(separator))
        nrow = len(widths)

        # print it
        for i in range(nrow):
            term.print(separator.join(nameStrs[j*nrow+i]
                                      +" "*(widths[i][j]-nameLens[j*nrow+i]) # fill in space
                                      for j in range(len(widths[i]))))

    def _print_list(self, items, term):
        """Print detailed list of H5 items, one item per row."""

        nameStrs, nameLens, details = self._compile_data(items, term)
        maxNameLen = max(nameLens)
        for i in range(len(nameStrs)):
            term.print(nameStrs[i]+" "*(maxNameLen-nameLens[i])+details[i])

    def _compile_data(self, items, term):
        """
        Sort items, attach colour codes and build detailled information.
        Returns:
            Tuple of list of names with colour codes, list of name lengths w/o
            colour codes, and list of detailled information.
        """
        
        nameStrs = []  # the string to be printed
        nameLens = []  # length of string without colour codes
        details = []   # extra stuff to be printed after names

        # build lists
        for name, item in sorted(items.items()):
            if item.kind == item.Kind.dataset:
                nameStr, nameLen = self._format_dataset_name(name, term)
                detail = "      {"+", ".join(str(x) for x in item.shape) \
                         +"} ("+str(item.dtype)+")"
            elif item.kind == item.Kind.group:
                nameStr, nameLen = self._format_group_name(name, term)
                detail = ""
            elif item.kind == item.Kind.softLink:
                nameStr, nameLen = self._format_softlink_name(name, term)
                detail = "  ->  "+item.target
            elif item.kind == item.Kind.externalLink:
                nameStr, nameLen = self._format_externallink_name(name, term)
                detail = "  ->  "+term.coloured(item.target[0], term.Colour.iwhite) \
                         +"//"+item.target[1]
            elif item.kind == item.Kind.hardLink:
                raise NotImplemented  # TODO

            nameStrs.append(nameStr)
            nameLens.append(nameLen)
            details.append(detail)

        return (nameStrs, nameLens, details)

    def _format_dataset_name(self, name, term):
        """Returns name with colour codes and length w/o them for datasets."""
        return (name, len(name))

    def _format_group_name(self, name, term):
        """Returns name with colour codes and length w/o them for groups."""
        return (term.coloured(name, term.Colour.iblue)+"/",
                len(name)+1)

    def _format_softlink_name(self, name, term):
        """Returns name with colour codes and length w/o them for soft links."""
        return (term.coloured(name, term.Colour.icyan)+"@",
                len(name)+1)

    def _format_externallink_name(self, name, term):
        """Returns name with colour codes and length w/o them for external links."""
        return (term.coloured(name, term.Colour.cyan)+"@",
                len(name)+1)
