#!/usr/bin/env bash

set -e

wd="$(mktemp -d)"

pdftk "$1" output "$wd/uncompressed.pdf" uncompress

rm_wm_sedexp=""
while read -r pattern; do
	echo "remove watermark string $pattern"
	rm_wm_sedexp+="s|$pattern||;"
done < <(sed -En 's/\\/\\\\/g;s/^\((.+)\) Tj$/\1/p' "$wd/uncompressed.pdf" | sort -u)

sed "$rm_wm_sedexp" < "$wd/uncompressed.pdf" | pdftk - output unwatermarked.pdf compress
echo "output to unwatermarked.pdf"

rm -r "$wd"
