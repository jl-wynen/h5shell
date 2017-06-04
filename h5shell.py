
import os
import fileinput

import re


import h5py as h5

import argparse

import vt100

# def run():
#     for line in fileinput.input("-"):
#         aux = line.strip()
#         history.append(aux)

        # cmd = re.split("[ \t]", aux)
        # cmd = re.split(r"'[^']+'|\"[^\"]+\"", aux)
        # cmd = re.split(r'"[^"]+"', aux)
        # print(cmd)

        # print(re.findall(r'(?:[^\s,"\']|["\'](?:\\.|[^"\'])*["\'])+', "'a d a \"c asd\""))

        # print(re.findall(r"(?P<quote>['\"]).*?(?P=quote)", "a 'b c'"))
        # print(re.findall(r"(?:[^\s\"']|(?P<quote>['\"])(?:\\.|[^\"'])*(?P=quote))", "a 'b c'"))
        # print(re.findall(r"(?:([^\s\"'])|('(?:\\.|[^\"'])*'))", "a 'b c'"))

        # l = [s for s in
             # re.split(r"([\w(\\.)]+|(?P<quote>[\"'])(?:\\.|[^(?P=quote)])*(?P=quote))", r"ab'b c'")
             # if s and s.strip() and s != "'" and s != '"']
        # print(l)

def split_args(args):
    return [s for s in
            re.split(r"([\w(\\.)]+|(?P<quote>[\"'])(?:\\.|[^(?P=quote)])*(?P=quote))",
                     args)
            if s and s.strip() and s != "'" and s != '"']

term = vt100.VT100()
with term.activate():
    while True:
        inp = split_args(term.get_input())

        if inp and inp[0].strip() == "exit":
            break
        
        term.print("input: ", inp)
    term.print(term.history.dump())


def run():
    fd = sys.stdin.fileno()
    oldattrs = termios.tcgetattr(fd)
    newattrs = termios.tcgetattr(fd)

    # print(0xC2, 0x9B)
    # sys.exit(0)
    
    try:
        tty.setraw(fd)
        
        while True:
            c = sys.stdin.read(1)

            if c == ESC:
                n = sys.stdin.read(1)
                if n == "[":
                    n = sys.stdin.read(1)
                    if ord(n) >= 64 and ord(n) <= 95:
                        print(r"^["+n, end="\r\n") # captures curos movement for n in [A,B,C,D]
                    else:
                        print("too long escape sequence with n = '"+n+"'", end="\r\n")
                else:
                    print("unknown escape sequence with n = '"+n+"'",end="\r\n")
            
            print('"'+c+'" - ',ord(c), end="\r\n")
            
            if c == 'q' or c == EOT:
                break

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, oldattrs)

    

def parse_args():
    parser = argparse.ArgumentParser(description="Testing an HDF5 shell")
    parser.add_argument("file", help="File to open")
    return parser.parse_args()

# if __name__ == "__main__":
    # args = parse_args()
    # fname = args.file

    # run()


# parser = argparse.ArgumentParser(description="calculate a suqre")

# parser.add_argument("square", help="display the square of it",
#                     type=int)
# parser.add_argument("-v","--verbose", "-x", "--extra" , help="speak to me!", action="store_true")

# args = parser.parse_args()

# if args.verbose:
#     print(args.square**2)


