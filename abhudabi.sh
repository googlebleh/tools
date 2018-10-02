#!/bin/bash

set -ex

se_regex='s/.*\.[sS]([[:digit:]]+)[eE]([[:digit:]]+)\..*/\1\2/'
box_dav_root="https://dav.box.com/dav/Mine"

# box_dav_url="$box_dav_root/Backups/cwee/domo_arigato"
box_dav_url="$box_dav_root/Backups/cwee/villy_con_sally"
recipient="2gbleh@gmail.com"

# box_dav_url="$box_dav_root/abhinans/Villy%20con%20Sally"
# recipient="abhinand.sukumar@gmail.com"

for fpath in "$@"; do
  fname=$(basename -- "$fpath")
  short_fname=$(echo $fname | sed -E "$se_regex")
  ul_url="$box_dav_url/$short_fname.gpg"
  gpg -o - -e -r "$recipient" "$fpath" | curl -nT - "$ul_url"
done
