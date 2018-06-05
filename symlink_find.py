#!/usr/bin/python3

import argparse
import os
import sys


def symlink_find(substring, root_path):
    try:
        for de in os.scandir(root_path):
            if de.is_dir(follow_symlinks=False):
                symlink_find(substring, de.path)
            elif de.is_symlink():
                try:
                    resolved_path = os.readlink(de.path)
                except OSError as e:
                    print(e.strerror, file=sys.stderr)
                    continue

                if substring in resolved_path:
                    print(de.path)
                    print(" -->", resolved_path)

    except OSError as e:
        print(e.strerror, file=sys.stderr)
        return


def getargs():
    long_desc = "Find symlinks by substrings of their resolved paths"
    def check_isdir(p):
        if os.path.isdir(p):
            return p
        raise argparse.ArgumentTypeError("invalid path: {!r}".format(p))

    ap = argparse.ArgumentParser(description=long_desc)
    ap.add_argument("-p", "--path", type=check_isdir, default=os.getcwd(),
                    help="root path to start searching")
    ap.add_argument("substring", help="substring of path to search for")
    return ap.parse_args()


def main():
    args = getargs()
    symlink_find(args.substring, args.path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
