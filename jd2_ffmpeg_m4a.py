#!/usr/bin/python3

from argparse import ArgumentParser

ap = ArgumentParser()
ap.add_argument("-i", action="append")
args = ap.parse_args()

print(str(args))
args.i[1] = "YAAS"
print(str(args))
