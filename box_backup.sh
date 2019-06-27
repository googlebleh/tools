#!/bin/bash

set -x

recipient="2gbleh@gmail.com"
box_dav_root="https://dav.box.com/dav/Mine/work"

box_dst_url="$box_dav_root/$2"
fpath="$1"
fname=$(basename -- "$fpath")
name=$(extstrip $fname)

ul_url="$box_dst_url/$name.tar.lz4.gpg"
tar -cf - "$fpath" | lz4 | gpg -e -r "$recipient" | curl -nT - "$ul_url"
