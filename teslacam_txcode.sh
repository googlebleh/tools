#!/bin/bash

set -e

if [ $# -ne "1" ]; then
    echo "error: args"
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
    # x265 already takes advantage of multi-core, use parallel for easy resume
    parallel -j 1 --joblog hevc.joblog --resume-failed --bar "nice $1"
}

remove_invalid ()
{
    local fpath=$1
    if [ ! -f "${fpath}" ]; then
        echo "invalid fpath=${fpath}"
        return 1
    fi

    if ffprobe -loglevel error "${fpath}"; then
        return 0
    fi
    local rv=$?

    local fsize=$(stat -c '%s' "${fpath}")
    if [ "${fsize}" == "595" ] || [ "${fsize}" == "0" ]; then
        echo "rm corrupted: ${fpath}"
        # rm "${fpath}"
        return 0
    fi

    echo "fail ${rv}: ${fpath}"
    return ${rv}
}

check_invalids ()
{
    local input_fpaths=$(list_input_subtree "${input_root_dpath}")
    # local parallel_cmd="ffprobe -loglevel error ${input_root_dpath}/{}"
    local parallel_cmd="remove_invalid ${input_root_dpath}/{}"
    export -f remove_invalid

    parallel --bar --halt now,fail=1 "${parallel_cmd}" ::: ${input_fpaths}
}

echo "Checking input files..."
invalid_log=invalids.txt
check_invalids | tee ${invalid_log}
if [ "$(stat -c '%s' ${invalid_log})" == "0" ]; then
    rm "${invalid_log}"
else
    echo "unhandled invalid inputs in ${invalid_log}"
    exit
fi

# mirror directory tree structure
find "${input_root_dpath}" -type d -printf "${output_root_dpath}/%P\0" |
    xargs -0 mkdir -p

ffmpeg_cmd="ffmpeg -y -i ${input_root_dpath}/{} -c:v libx265 -c:a copy ${output_root_dpath}/{.}.mkv"
list_input_subtree "${input_root_dpath}" | sort | parallel_wrap "${ffmpeg_cmd}"

day_regex=".*\(Saved\|Sentry\)Clips/[0-9]\{4\}\([-_][0-9]\{2\}\)\{5\}"
find "${output_root_dpath}"              \
    -depth                               \
    -type d                              \
    -regextype sed -regex "${day_regex}" \
    -execdir tar -cf '{}'{.tar,} \;      \
    -execdir rm -r '{}' \;
