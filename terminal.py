import re

def split_args(args):
    return [s for s in
            re.split(r"([\w(\\.)]+|(?P<quote>[\"'])(?:\\.|[^(?P=quote)])*(?P=quote))",
                     args)
            if s and s.strip() and s != "'" and s != '"']
