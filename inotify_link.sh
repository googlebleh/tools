#!/usr/bin/env bash

# mirror one directory to another
# todo: delete files too

while inotifywait -qq --event modify,create,delete,move --recursive "$1"; do
	find "$1" -mindepth 1 -type d -printf "$2/%P\0" | xargs -0 mkdir -p
	find "$1" -mindepth 1 -type f -printf "%P\0" | xargs -0 -I % ln "$1/%" "$2/%" 2>/dev/null
done
