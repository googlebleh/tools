#!/usr/bin/env python3

import subprocess
import re


target_name = "bluez_card.94_DB_56_88_E9_8F"
target_headset_profile = "headset_head_unit"
target_audio_profile = "a2dp_sink"


def set_profile(card_name, profile):
    cmd = ["pacmd", "set-card-profile", card_name, profile]
    subprocess.run(cmd, check=True)


cp = subprocess.run(["pacmd", "list-cards"], capture_output=True, text=True)

index = None
name = None
active_profile = None
for line in cp.stdout.split("\n"):

    if name == target_name and active_profile is not None:
        if active_profile == target_headset_profile:
            set_profile(target_name, target_audio_profile)
        elif active_profile == target_audio_profile:
            set_profile(target_name, target_headset_profile)
        else:
            print("unknown profile:", active_profile)
        break

    index_m = re.match(r"\s*index: (\d+)", line)
    if index_m:
        index = int(index_m.group(1))
        name = None
        active_profile = None
        continue

    name_m = re.match(r"\s*name: <([^<>\n]+?)>", line)
    if name_m:
        name = name_m.group(1)
        continue

    active_profile_m = re.match(r"\s*active profile: <([^<>\n]+?)>", line)
    if active_profile_m:
        active_profile = active_profile_m.group(1)
        continue
