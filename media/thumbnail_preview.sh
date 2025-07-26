#!/bin/bash
set -e

# Check if video path is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <video_file>"
  exit 1
fi

# Assign the input video file path and output folder
fpath="$1"
output_dir="$2"

fname=$(basename "$fpath")
output_file="${output_dir}/${fname%.*}.png"

# Ensure the output directory exists
mkdir -p "$output_dir"

# Get the duration of the video in seconds
duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$fpath")

# Check if ffprobe could get the duration
if [ -z "$duration" ]; then
  echo "Error: Could not get video duration."
  exit 1
fi

# Calculate the frame rate to extract 20 evenly spaced frames
fps=$(echo "scale=6; 20 / $duration" | bc)

# Run ffmpeg to extract and tile the frames
ffmpeg \
  -loglevel error \
  -hwaccel cuda \
  -i "$fpath" \
  -vf "fps=$fps,scale=320:-1,tile=5x4:padding=2:color=white" \
  -frames:v 1 "$output_file"
