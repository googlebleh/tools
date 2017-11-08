#!/usr/bin/env bash

set -e

utd_str="Already up-to-date."
ctags_v_regex='s/Universal Ctags ([[:digit:].]+)\(.+/\1/'


if [[ $(git pull) =~ $utd_str ]]; then
    echo $utd_str
    exit  # no update available
fi

# build ctags
./autogen.sh
./configure
make

# extract version number
ctags_v=$(./ctags --version | head -n 1 | sed -E "$ctags_v_regex")

# rm old version and install new one
if apt list ctags | grep -q "installed,local"; then
    sudo apt -y remove ctags
fi
sudo checkinstall --deldoc=yes --deldesc=yes --pkgversion=$ctags_v --exclude=.
