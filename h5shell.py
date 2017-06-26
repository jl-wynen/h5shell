import argparse

from shell import Shell
from util import *

try:
    from vt100 import VT100 as Term
except ImportError:
    from terminal import Terminal as Term

# def split_args(args):
#     return [s for s in
#             re.split(r"([\w(\\.)]+|(?P<quote>[\"'])(?:\\.|[^(?P=quote)])*(?P=quote))",
#                      args)
#             if s and s.strip() and s != "'" and s != '"']

    

def parse_args():
    parser = argparse.ArgumentParser(description="Testing an HDF5 shell")
    parser.add_argument("FILE", help="File to open")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    fname = args.FILE

    
    shell = Shell(Term())
    shell.run(fname)


# parser = argparse.ArgumentParser(description="calculate a suqre")

# parser.add_argument("square", help="display the square of it",
#                     type=int)
# parser.add_argument("-v","--verbose", "-x", "--extra" , help="speak to me!", action="store_true")

# args = parser.parse_args()

# if args.verbose:
#     print(args.square**2)


