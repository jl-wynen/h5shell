def table_layout(lens, maxWidth, separatorLength=1):
    """
    Builds a 2 dimensional table layout for 1 dimensional data.

    The table is layed out in column major order such that the given items
    fit into the given maximum width. If Items do not fit, the returned
    widths are the maximum of lens.

    Args:
        lens (:obj:`list` of int): Lengths of all items to be layed out.
        maxWidth (int): Maximum width for the table.
        separatorLength (int, optional): Length of the separator between items.

    Returns:
        List of lists of widths. ``table_layout(...)[i][j]`` gives the width of
        element ``(i,j)`` in the table.
    """

    # i and j are row and column indices, respectively.
    # m and n are number of rows and columns, repsectively.
    #  n does not include columns that are not completely filled.
    
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
    Prints a table of strings.

    Args:
        strs (:obj:`list` of :obj:`str`): Strings to print.
        maxWidth (int): Maximum width to use for the table.
        separator (:obj:`str`, optional): String that separates list entries.
        prnt (function, optional): Function to use for printing.
    """
    
    widths = table_layout([len(s) for s in strs], maxWidth, len(separator))
    m = len(widths)

    for i in range(m):
        prnt(separator.join("{{:<{:d}}}".format(widths[i][j]).format(strs[j*m+i])
                            for j in range(len(widths[i]))))
