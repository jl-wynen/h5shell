"""
Module for ls command.
"""

from . import command

from h5sh.util import table_layout

class ls(command.Command):
    """Command to list items"""

    def __init__(self):
        super(ls, self).__init__()

        self._parser = command.Command.Parser(prog="ls",
                                              description="List information about HDF5 items.")
        self._parser.add_argument("item", nargs="*", default=["."],
                                  help="Item(s) to list  (the current group by default).")
        self._parser.add_argument("-l", help="show extra information", action="store_true")

    def __call__(self, args, wd, h5mngr, term):
        """Execute the ls command."""

        pa = self._parse_args(args, term)
        if not pa:
            return

        pathsAndItems = h5mngr.get_items(wd, *pa.item)

        # show names of groups before listing contents
        printGroupNames = len(pathsAndItems) > 1
        first = True
        for path, items in pathsAndItems:
            if not path:
                path = ["/"]

            if not first:
                # separate entries
                term.print("")

            if items: # skip empty groups
                if printGroupNames:
                    term.print("/".join(path)+"/:")

                if pa.l:
                    _print_list(items, term)
                else:
                    _print_plain(items, term)

                first = False


def _print_plain(items, term):
    """Print table of H5 items."""

    nameStrs, nameLens, _ = _compile_data(items, term)

    # build layout w/o respecting colour codes
    separator = "   "
    widths = table_layout(nameLens, term.get_width(), len(separator))
    nrow = len(widths)

    # print it
    for i in range(nrow):
        term.print(separator.join(nameStrs[j*nrow+i]
                                  +" "*(widths[i][j]-nameLens[j*nrow+i]) # fill in space
                                  for j in range(len(widths[i]))))

def _print_list(items, term):
    """Print detailed list of H5 items, one item per row."""

    nameStrs, nameLens, details = _compile_data(items, term)
    maxNameLen = max(nameLens)
    for i in range(len(nameStrs)):
        term.print(nameStrs[i]+" "*(maxNameLen-nameLens[i])+details[i])

def _compile_data(items, term):
    """
    Sort items, attach colour codes and build detailled information.

    :returns:
        Tuple of:
         * list of names with colour codes
         * list of name lengths w/o colour codes
         * list of detailled information.
    """

    nameStrs = []  # the string to be printed
    nameLens = []  # length of string without colour codes
    details = []   # extra stuff to be printed after names

    # build lists
    for name, item in sorted(items.items()):
        if item.kind == item.Kind.dataset:
            nameStr, nameLen = _format_dataset_name(name, term)
            detail = "      {"+", ".join(str(x) for x in item.shape) \
                     +"} ("+str(item.dtype)+")"
        elif item.kind == item.Kind.group:
            nameStr, nameLen = _format_group_name(name, term)
            detail = ""
        elif item.kind == item.Kind.softLink:
            nameStr, nameLen = _format_softlink_name(name, term)
            detail = "  ->  "+item.target
        elif item.kind == item.Kind.externalLink:
            nameStr, nameLen = _format_externallink_name(name, term)
            detail = "  ->  "+term.coloured(item.target[0], term.Colour.iwhite) \
                     +"//"+item.target[1]
        elif item.kind == item.Kind.hardLink:
            raise NotImplementedError()  # TODO

        nameStrs.append(nameStr)
        nameLens.append(nameLen)
        details.append(detail)

    return (nameStrs, nameLens, details)

def _format_dataset_name(name, term):
    """Returns name with colour codes and length w/o them for datasets."""
    return (name, len(name))

def _format_group_name(name, term):
    """Returns name with colour codes and length w/o them for groups."""
    return (term.coloured(name, term.Colour.iblue)+"/",
            len(name)+1)

def _format_softlink_name(name, term):
    """Returns name with colour codes and length w/o them for soft links."""
    return (term.coloured(name, term.Colour.icyan)+"@",
            len(name)+1)

def _format_externallink_name(name, term):
    """Returns name with colour codes and length w/o them for external links."""
    return (term.coloured(name, term.Colour.cyan)+"@",
            len(name)+1)
