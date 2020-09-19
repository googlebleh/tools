#!/usr/bin/env python3

import argparse
import os


def ln_parent(src_fpath, dst_rootdir):
    parent_path, src_fname = os.path.split(src_fpath)

    dst_dpath = os.path.join(dst_rootdir, parent_path)
    if args.force:
        os.makedirs(dst_dpath, exist_ok=True)
    print('$ mkdir -p "{}"'.format(dst_dpath))

    dst_fpath = os.path.join(dst_dpath, src_fname)
    assert dst_fpath == os.path.join(dst_rootdir, src_fpath)
    if os.path.exists(dst_fpath):
        return False
    if args.force:
        os.link(src_fpath, dst_fpath)
    print('$ ln "{}" "{}"'.format(src_fpath, dst_fpath))
    print()

    return True


def getargs():
    desc = "mimic `cp --parent` behavior for making hard links"
    ap = argparse.ArgumentParser(description=desc)
    ap.add_argument("-f", "--force", action="store_true")
    ap.add_argument("sources", nargs="+")
    ap.add_argument("dest_root")
    return ap.parse_args()


def main():
    for fpath in args.sources:
        if not ln_parent(fpath, args.dest_root):
            print("FAIL")
            return 1

    return 0


if __name__ == "__main__":
    args = getargs()
    main()
