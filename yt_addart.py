#!/usr/bin/python3

import glob
import os
import re
import sys
from argparse import ArgumentParser

from mutagen.mp4 import MP4, MP4Cover


def find_art(song_fname, art_fpaths):
    song_name, _ = os.path.splitext(song_fname)
    m = re.match(r"\d+ (.+)", song_name)
    song_title = m.group(1)
    for fpath in art_fpaths:
        fname = os.path.basename(fpath)
        if song_title in fname:
            return fpath
    return None


def process_args():
    ap = ArgumentParser()
    ap.add_argument("input_dir")
    return ap.parse_args()


def main():
    MP4_COVER_KEY = "covr"

    args = process_args()

    audio_fpaths = glob.glob(os.path.join(args.input_dir, "*.m4a"))
    image_fpaths = glob.glob(os.path.join(args.input_dir, "*.jpg"))

    for song_fpath in audio_fpaths:
        song_info = MP4(song_fpath)
        if MP4_COVER_KEY in song_info:
            print("Art exists for", song_fpath)
            continue

        song_fname = os.path.basename(song_fpath)
        art_fpath = find_art(song_fname, image_fpaths)

        with open(art_fpath, "rb") as f:
            song_cover = MP4Cover(f.read(), imageformat=MP4Cover.FORMAT_JPEG)
            song_info[MP4_COVER_KEY] = [song_cover]
        song_info.save()
        os.remove(art_fpath)

    return 0


if __name__ == '__main__':
    sys.exit(main())
