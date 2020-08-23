#!/usr/bin/env python3

import argparse
import json
import os
import shutil
import subprocess
import tempfile


def touch_tempfile():
    fd, fpath = tempfile.mkstemp()
    os.close(fd)
    return fpath


##
# @brief Get "subtitle index" in softsubbed video file.
# @details Prioritize subtitle tracks as follows:
#           - marked SDH
#           - with the greatest number of frames
def get_sub_i(fpath, language):
    cmd = [
        "ffprobe",
        "-loglevel", "quiet",
        "-of", "json",
        "-show_streams",
        "-select_streams", "s",
        fpath,
    ]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, _ = p.communicate()
    if p.returncode:
        return None

    ffprobe = json.loads(stdout.decode())
    min_index = 6969 # INT_MAX
    max_frames = -1
    index = None
    done = False
    for stream in ffprobe["streams"]:
        if stream["index"] < min_index:
            min_index = stream["index"]

        if (not done) and stream["tags"]["language"] == language:
            # prioritize SDH subs. exit early.
            if stream["tags"].get("title") == "SDH":
                index = stream["index"]
                done = True
                continue

            # find sub track with most "frames"?
            # ffprobe outputs this value as a string
            if int(stream["tags"]["NUMBER_OF_FRAMES-eng"]) > max_frames:
                index = stream["index"]
                max_frames = int(stream["tags"]["NUMBER_OF_FRAMES-eng"])

    if index is None:
        # language not found
        return None
    else:
        return (index - min_index)


def getargs():
    long_desc = "Hardcode subtitles in video files in-place"
    ap = argparse.ArgumentParser(description=long_desc)
    ap.add_argument("input_fpaths", nargs="+")
    # ap.add_argument("output_dir")
    return ap.parse_args()


def main():
    args = getargs()
    for fpath in args.input_fpaths:
        # ffmpeg has trouble with subtitle file paths containing spaces,
        # so pass it a temporary symlinked version
        abs_fpath = os.path.realpath(fpath)
        subs_fpath = touch_tempfile()
        os.remove(subs_fpath)
        os.symlink(abs_fpath, subs_fpath)

        sub_i = get_sub_i(fpath, "eng")
        _, ext = os.path.splitext(fpath)
        output_fpath = touch_tempfile() + ext
        p = subprocess.Popen([
            "ffmpeg", "-y",
            "-i", fpath,
            "-vf", "subtitles={}:si={:d}".format(subs_fpath, sub_i),
            "-c:a", "copy",
            output_fpath,
        ])
        p.wait()

        os.remove(fpath)
        os.remove(subs_fpath)
        shutil.move(output_fpath, fpath)


if __name__ == "__main__":
    main()
