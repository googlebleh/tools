#!/usr/bin/env python

import os
import shutil
from argparse import ArgumentParser
from datetime import datetime


ap = ArgumentParser(description="Make timestamped clones of files.")
ap.add_argument("file_paths", nargs="+", help="paths to files to clone")
args = ap.parse_args()

time_suffix = datetime.now().strftime("-%y%m%d_%H%M%S")
for fpath in args.file_paths:
    path_name, ext = os.path.splitext(fpath)
    shutil.copy(fpath, path_name + time_suffix + ext)
