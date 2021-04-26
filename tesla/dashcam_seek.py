#!/usr/bin/env python3

import datetime
import glob
import json
import os
import subprocess
from argparse import ArgumentParser


class Main:
    def __init__(self):
        ap = ArgumentParser("View a dashcam capture.")
        ap.add_argument("-c", "--camera",
                        help="force which camera")
        ap.add_argument("-i", "--input-dir", default=".")
        self.args = ap.parse_args()

        self.attention_span = 5  # seconds

    @staticmethod
    def get_camera_name(event_json):
        lut = {
            "0": "front",
            "1": "front",
            "2": "front",
            "3": "front",
            "4": "front",
            "5": "left_repeater",
            "6": "right_repeater",
            "7": "front",
        }
        number = event_json["camera"]
        return lut[number]

    def get_vid_ts(self, fpath):
        fname = os.path.basename(fpath)

        time_fmt = "%Y-%m-%d_%H-%M-%S" + self.vid_suffix
        return datetime.datetime.strptime(fname, time_fmt)

    def run(self):
        event_fpath = os.path.join(self.args.input_dir, "event.json")
        with open(event_fpath) as f:
            event_json = json.load(f)

        ts_str = event_json["timestamp"]
        event_ts = datetime.datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S")

        if self.args.camera is not None:
            camera_name = self.args.camera
        else:
            camera_name = Main.get_camera_name(event_json)
        self.vid_suffix = f"-{camera_name}.mp4"

        # find video containing event
        vids = sorted(glob.glob("*" + self.vid_suffix))
        index_to_play = len(vids) - 1
        for i in range(1, len(vids)):
            if self.get_vid_ts(vids[i]) >= event_ts:
                index_to_play = i - 1

        # play video containing event first
        event_vid = vids.pop(index_to_play)
        vids.insert(0, event_vid)

        # seek to just before event
        event_vid_ts = self.get_vid_ts(event_vid)
        event_offset = event_ts - event_vid_ts
        start_time = event_offset.total_seconds() - self.attention_span

        print("Opening", event_vid_ts)
        print("\twith event at", event_offset)
        print()

        cmd = ["vlc", f"--start-time={start_time}"] + vids
        subprocess.run(cmd)


if __name__ == "__main__":
    Main().run()
