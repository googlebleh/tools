#!/bin/bash

set -e

if [ $# -ne "1" ]; then
    exit 1
fi


# first arg without trailing slash
input_root_dpath="${1%/}"

output_root_dpath="${input_root_dpath}-hevc"


list_input_subtree ()
{
    find "$1" -type f -name "*.mp4" -printf '%P\n'
}

parallel_wrap ()
{
    parallel -j 1 --joblog hevc.joblog --resume-failed --bar "nice $1"
}

check_invalids ()
{
    local input_fpaths=$(list_input_subtree "${input_root_dpath}")
    local parallel_cmd="ffprobe -loglevel error ${input_root_dpath}/{}"
    parallel --halt now,fail=1 "${parallel_cmd}" ::: ${input_fpaths}
}

check_invalids

# mirror directory tree structure
find "${input_root_dpath}" -type d -printf "${output_root_dpath}/%P\0" |
    xargs -0 mkdir -p

# x265 already takes advantage of multi-core, use parallel for easy resume
ffmpeg_cmd="ffmpeg -y -i ${input_root_dpath}/{} -c:v libx265 -c:a copy ${output_root_dpath}/{.}.mkv"
list_input_subtree "${input_root_dpath}" | sort | parallel_wrap "${ffmpeg_cmd}"

day_regex=".*\(Saved\|Sentry\)Clips/[0-9]\{4\}\([-_][0-9]\{2\}\)\{5\}"
find "${output_root_dpath}"              \
    -depth                               \
    -type d                              \
    -regextype sed -regex "${day_regex}" \
    -execdir tar -cf '{}'{.tar,} \;      \
    -execdir rm -r '{}' \;
