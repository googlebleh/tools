#!/bin/bash

set -e

se_regex='s/.*\.[sS]([[:digit:]]+)[eE]([[:digit:]]+)\..*/\1\2/'
box_dav_root="https://dav.box.com/dav/Mine/Backups"

# box_dav_url="$box_dav_root/cwee/domo_arigato"
# box_dav_url="$box_dav_root/cwee/villy_con_sally"
# recipient="2gbleh@gmail.com"

box_dav_url="$box_dav_root/abhinans/tgt/1280_720"
recipient="abhinand.sukumar@gmail.com"

for fpath in "$@"; do
  fname=$(basename -- "$fpath")
  short_fname=$(echo $fname | sed -E "$se_regex")
  ul_url="$box_dav_url/$short_fname.gpg"
  echo "${ul_url}"
  gpg --trust-model always -o - -e -r "$recipient" "$fpath" | curl -nT - "$ul_url"
done
