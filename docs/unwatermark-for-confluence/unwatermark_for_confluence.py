#!/usr/bin/env python3

import os
import re
import subprocess
import sys

fpath = sys.argv[1]
dpath, fname = os.path.split(fpath)

print("uncompressing")
cmd = ["pdftk", fpath, "output", "-", "uncompress"]
cp = subprocess.run(cmd, capture_output=True, check=True)
in_bytes = cp.stdout

def get_image_regex(length):
    regex_bytes = r"""<<[^>]+
                  /Height\ 320[^>]+
                  /Width\ 445[^>]+
                  /Length\ ({})[^>]+
                  >>\n
                  stream\n
                  (.+?)\n # binary stream
                  endstream""".format(length).encode()
    return re.compile(regex_bytes, re.DOTALL | re.VERBOSE)

watermark_regex = get_image_regex(427200)
blank_image_length = 142400
blank_image_regex = get_image_regex(blank_image_length)

print("inspecting watermark strategy")
m = blank_image_regex.search(in_bytes)
if m is None:
    print("fail: couldn't find blank image")
    sys.exit(1)
blank_image_stream = m.group(2)

def overwrite_watermark(m):
    match_s = m.group(1)
    length_begin = m.start(1)
    length_end = m.end(1)
    stream_begin = m.start(2)
    stream_end = m.end(2)
    return match_s[:length_begin] \
        + str(blank_image_length).encode() \
        + match_s[length_end:stream_begin] \
        + blank_image_stream \
        + match_s[stream_end:]

print("clearing watermark")
unwatermarked_pdf, _ = watermark_regex.subn(overwrite_watermark, in_bytes)

compressed_fpath = os.path.join(dpath, f"unwatermarked-{fname}")
print("fixing up and compressing output PDF to", repr(compressed_fpath))
cmd = ["pdftk", "-", "output", compressed_fpath, "compress"]
subprocess.run(cmd, input=unwatermarked_pdf, check=True)
