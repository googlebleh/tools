#!/bin/bash

set -e

for fpath in "$@" do
    name=`extstrip.py $fpath`
    ffmpeg -i "$fpath" -tune animation -c:a libfdk_aac -c:s copy "$name_reenc.mkv"
done
