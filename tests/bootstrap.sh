#!/bin/sh
#
# running this script is required before testing will work.
# setup.py should take care of that.

./linearize data/viking.dox 0 200 3 data/viking.dox.linear
./linearize data/viking.d01 7 400 5 data/viking.d01.linear
./linearize data/viking.til 0 16000 4 data/viking.til.linear
./spliceattack data/viking.dt6 data/attack.bin data/attack.full