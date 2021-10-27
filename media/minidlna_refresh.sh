#!/usr/bin/env bash

# Workaround when `minidlnad -R` doesn't work
#
# inspired by: https://raspberrypi.stackexchange.com/a/83133/139101


touchme ()
{
    set -e

    local fpath="$1"
    local save_fpath="$1.touchme_bak"

    mv "$fpath" "$save_fpath"
    mv "$save_fpath" "$fpath"
}


export -f touchme
find -mindepth 1 -exec bash -c 'touchme "$0"' '{}' \;
