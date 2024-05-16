#!/usr/bin/env python3

##
# @file sshconfig_includeall.py
# @brief Some tools / environments don't support ssh_config's `Include`
#        keyword. This script should "flatten" an ssh_config, converting
#        it to one that uses includes into an expanded one that imports
#        all the included lines into one file.

import fileinput
import os

sshconfig_dpath = os.path.join(os.getenv("HOME"), ".ssh")


def include_path(path):
    fpath = os.path.expanduser(path)
    cwd_save = os.getcwd()

    os.chdir(sshconfig_dpath)
    f = open(fpath)
    os.chdir(cwd_save)

    return f


def expand_lines(lines):
    for line in lines:
        # could use a regex that ignores leading whitespace
        if line.strip().startswith("Include "):
            config_path = line.strip()[len("Include "):]
            included_lines = include_path(config_path)
            yield from expand_lines(included_lines)
        else:
            yield line


if __name__ == "__main__":
    expanded = expand_lines(fileinput.input())
    print(''.join(expanded), end="")
