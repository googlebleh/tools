#!/usr/bin/python3

import sys
import os
import subprocess
from argparse import ArgumentParser

# parse command-line args
ap = ArgumentParser()
cwd = os.getcwd()
ap.add_argument("-o", "--output-dir", default=cwd)
ap.add_argument("input_files", nargs="+", default=cwd)
args = ap.parse_args()


for fpath in args.input_files:
    name, _ = os.path.splitext(os.path.basename(fpath))
    output_fpath = os.path.join(args.output_dir, name + ".m4a")
    cmd = [
        "ffmpeg",
        "-i", fpath,
        "-vn",  # no video
        # "-ac", "2",  # num of audio channels
        # "-af", "volume=0.5",
        "-c:a", "libfdk_aac",  # Fraunhofer AAC
        "-vbr", "4",  # http://wiki.hydrogenaud.io/index.php?title=Fraunhofer_FDK_AAC#Bitrate_Modes
        output_fpath,
    ]
    print(' '.join(cmd))
    subprocess.run(cmd)
    print()
