#!/usr/bin/env python
import sys
import os

import nohrio.scripts #.ohrrpgce import *

def usage():
    sys.exit("""Usage:  decompile.py <.hs/.hsp file> [script id or name]
If no script is specified, prints a list of script ids and names.

Warning: decompile results likely won't compile. In particular, 'for' and
'switch' aren't decompiled to valid HS syntax, and plotstrings are lost""")
if len(sys.argv) <= 1:
    usage()

if not os.path.isfile(sys.argv[1]):
    print(sys.argv[1], "not found\n")
    usage()

scripts = nohrio.scripts.HSScripts(sys.argv[1])
if len(sys.argv) > 2:
    whichscript = sys.argv[2]  # either an id or a name
    try:
        whichscript = int(whichscript)
    except:
        pass
    print(scripts.script(whichscript))
else:
    for id, name in sorted(scripts.scriptnames.items()):
        print("(%d %s)" % (id, name), end=' ')
