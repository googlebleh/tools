#!/usr/bin/python3

import sys
from argparse import ArgumentParser


def capture_args():
    ap = ArgumentParser()
    ap.add_argument("ff_args", nargs="*")
    return ap.parse_args()


def main():
    args = capture_args()

    new_args = []
    fmt_arg = False
    for arg in args.ff_args:
        if arg == "-f":
            fmt_arg = True
            #  drop arg

        elif fmt_arg:
            pass
        
        else:
            new_args.append(arg)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
