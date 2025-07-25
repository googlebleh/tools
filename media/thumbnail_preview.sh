#!/bin/bash
set -e

fpath="$1"
fname=$(basename "$fpath")

mkdir -p /tmp/screens
# ffmpeg -loglevel error -i "$fpath" -vf "select=not(mod(n\,20)),scale=200:-1,tile=5x4:padding=2:color=white" -vsync 0 -frames:v 1 "/tmp/screens/$fname.jpg"
ffmpeg -loglevel error -i "$fpath" -vf "select=not(mod(n\,20)),tile=5x4:padding=2:color=white" -vsync 0 -frames:v 1 "/tmp/screens/$fname.jpg"
