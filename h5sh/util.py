"""
Some utility functions that might be useful throughout the project.
"""

from posixpath import split

def table_layout(lens, maxWidth, separatorLength=1):
    """
    Build a 2 dimensional table layout for 1 dimensional data.

    The table is layed out in column major order such that the given items
    fit into the given maximum width. If Items do not fit, the returned
    widths are the maximum of lens.

    :param lens: List of lengths of all items to be layed out.
    :param maxWidth: Maximum width for the table.
    :param separatorLength: Length of the separator between items.

    :returns:
        List of lists of widths. ``table_layout(...)[i][j]`` gives the width of
        element ``(i,j)`` in the table.
    """

    # i and j are row and column indices, respectively.
    # m and n are number of rows and columns, repsectively.
    # n does not include columns that are not completely filled.

    N = len(lens)
    m = 1
    n = N//m
    while n > 0:

        # calculate widths of each fully filled column
        widthAux = [max(lens[j*m:(j+1)*m]) for j in range(n)]

        # combine with remainders
        widths = []
        for i in range(m):
            if i+n*m < N:
                widths.append(widthAux + [lens[i+n*m]])
            else:
                widths.append(widthAux)

        # compute maximum required width
        required = max(sum(w) + separatorLength*(len(w)-1) for w in widths)

        if required <= maxWidth:
            # fits, we are done here
            return widths

        # does not fit, try with one more row
        m += 1
        n = N//m

    # fallback if items do not fit
    return [[max(lens)]]*N

def print_table(strs, maxWidth, separator=" ", prnt=print):
    """
    Print a table of strings.

    :param strs: List of strings to print.
    :param maxWidth: Maximum width to use for the table.
    :param separator: String that separates list entries.
    :param prnt: Function to use for printing.
    """

    widths = table_layout([len(s) for s in strs], maxWidth, len(separator))
    m = len(widths)

    for i in range(m):
        prnt(separator.join("{{:<{:d}}}".format(widths[i][j]).format(strs[j*m+i])
                            for j in range(len(widths[i]))))

def split_path(spath):
    """
    Split a string representing a path into a list.
    The result can be partly undone by calling '/'.join(split_path(...))
    up to leading and trailing slashes.
    A leading slash is returned as an individual list element.

    :param spath: String representing the path.
    :returns: Split path as list of strings.
    """

    res = split(spath)  # split into (head, tail)
    path = [res[1]]  # tail is always completely split
    if res[0]:
        if res[0] == "/" or res[0] == "//": # at root
            path = ["/"] + path
        else:
            path = split_path(res[0]) + path  # split head again
    return path

def abspath(wd, path):
    """
    Turn path into an absolute path based on working directory wd.
    wd must already be an absolute path.
    """

    if not path:          # empty -> just wd
        result = wd[:]
    elif path[0] == "/":  # path relative to root
        result = []
        path = path[1:]
    else:                 # path relative to wd
        result = wd[:]

    for i, p in enumerate(path):
        if p == ".":
            continue
        elif p == "..":
            if result:  # just ignore it if moving out of file
                result = result[:-1]
        else:
            result.append(path[i])

    return result
