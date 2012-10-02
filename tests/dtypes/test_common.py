from unittest import TestCase
import nose
import functools
from oktest import ok
import nohrio.nohrio2 as nohrio
import os
from nohrio.iohelpers import FilelikeLump
from nohrio.dtypes.common import (ALL, PUBLIC, 
                                  scalararray, readstr,
                                  writestr, copyfrom,
                                  readint, writeint,
                                  StatList, PalettedPic,
                                  Coords)
from bits import showbitsets

class testCommon(TestCase):
    def testFoo(self):
        assert 0

if __name__ == "__main__":
    nose.main(defaultTest='test_common.py')
