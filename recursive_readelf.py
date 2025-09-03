#!/usr/bin/env python3

import argparse
import os
import re
import subprocess


class Main:
    def __init__(self):
        self.getargs()

        self.rpath_regex = re.compile(r"^\s*0x[0-9a-f]+\s+\(RUNPATH\)\s+Library runpath: \[(.+)\]$", re.MULTILINE)
        self.so_regex = re.compile(r"^\s*0x[0-9a-f]+\s+\(NEEDED\)\s+Shared library: \[(.+)\]$", re.MULTILINE)
        self.seen_elfs = set()

    def getargs(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("root_dpath")
        ap.add_argument("elf_fpath")
        ap.add_argument("--readelf", default="readelf")
        ap.add_argument("-v", "--verbose", action="store_true")
        self.args = ap.parse_args()

    def print_dependencies(self, elf_fpath, depth=0):
        self.seen_elfs.add(elf_fpath)

        cmd = [self.args.readelf, "-d", elf_fpath]
        cp = subprocess.run(cmd, capture_output=True, text=True)

        rpath_m = self.rpath_regex.search(cp.stdout)
        if rpath_m is None:
            rpath = None
        else:
            rpath = rpath_m.group(1)
            if len(self.rpath_regex.findall(cp.stdout)) > 1:
                print("WARN: multiple rpaths")

        so_names = {so_m.group(1) for so_m in self.so_regex.finditer(cp.stdout)}
        for dpath, dnames, fnames in os.walk(self.args.root_dpath):
            fnames = set(fnames)
            so_matches = so_names & fnames
            so_names -= fnames
            for fname in so_matches:
                so_path = os.path.join(dpath, fname)
                if so_path in self.seen_elfs:
                    continue
                if self.args.verbose:
                    print("    " * depth + so_path)
                else:
                    print(so_path)
                self.print_dependencies(so_path, depth + 1)
        for name in so_names:
            print("Not found:", name)


if __name__ == "__main__":
    m = Main()
    m.print_dependencies(m.args.elf_fpath)
