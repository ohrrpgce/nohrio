from unittest import TestCase
import nose
import functools
from oktest import ok
import nohrio.nohrio2 as nohrio
import os
from nohrio.iohelpers import FilelikeLump
from nohrio.dtypes.hero import Hero, BITSETS
from bits import showbitsets

class testHero(TestCase):
    def testFoo(self):
        assert 0

if __name__ == "__main__":
    nose.main(defaultTest='test_hero.py')
