#!/usr/bin/env python3

import nohrio.lump
import nohrio.reload
import sys
import os

if len(sys.argv) != 2:
    print("Prints a RELOAD file.")
    print("Usage: dumpreload.py <file.reld>")
    exit(1)

infile = sys.argv[1]

with open(infile, 'rb') as f:
    root = nohrio.reload.read(f)

print(root)

# with open('out.reld', 'wb') as of:
#     root.write_root(of)
