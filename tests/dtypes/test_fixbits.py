from unittest import TestCase
import nose
import functools
from oktest import ok
import nohrio.nohrio2 as nohrio
import os
from nohrio.iohelpers import FilelikeLump
from nohrio.dtypes.fixbits import FixBits
from bits import showbitsets

class testFixbits(TestCase):
    def testFoo(self):
        assert 0

if __name__ == "__main__":
    nose.main(defaultTest='test_fixbits.py')
