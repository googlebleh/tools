#!/usr/bin/python3

import sys
import os
import subprocess
from tempfile import NamedTemporaryFile

import pygments
from pygments import lexers
from pygments import formatters


# cfg
rtf2pdf_cmd = [
    "libreoffice", "--headless", "--invisible", "--norestore",
    "--convert-to", "pdf",  # "source-file.rtf"
]

# setup based on args
fpath = sys.argv[1]
ofpath = sys.argv[2]
rtf2pdf_cmd.append(ofpath)  # append input file to command above

# run pygments to get RTF
ml_lexer = lexers.get_lexer_by_name("matlab")
ml_formatter = formatters.get_formatter_by_name("rtf", fontface="Ubuntu Mono")
with open(fpath, "r") as input_f, open(ofpath, "w") as output_f:
    code = input_f.read()
    pygments.highlight(code, ml_lexer, ml_formatter, outfile=output_f)

# translate to PDF
subprocess.run(rtf2pdf_cmd)
os.remove(ofpath)  # delete intermediate rtf file
