from unittest import TestCase
import nose
import functools
from oktest import ok
import nohrio.nohrio2 as nohrio
import os
from nohrio.iohelpers import FilelikeLump
from nohrio.dtypes.npc import NPCDef, NPCLoc
from bits import showbitsets

class testNPCDef(TestCase):
    def testFoo(self):
        assert 0

class testNPCLoc(TestCase):
    def testFoo(self):
        assert 0


if __name__ == "__main__":
    nose.main(defaultTest='test_npc.py')
