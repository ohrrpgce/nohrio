from unittest import TestCase
import nose
import functools
from oktest import ok
import nohrio.nohrio2 as nohrio
import os
from nohrio.iohelpers import FilelikeLump
from bits import showbitsets
from nohrio.dtypes.attack import AttackData
from testutils import loadsaveok

class testAttack(TestCase):
    def testLoadSave(self):
        ok(loadsaveok(AttackData,
                      '../../ohrrpgce/vikings/vikings.rpgdir/viking.pal')) == True

    def testFoo(self):
        assert 0

if __name__ == "__main__":
    nose.main(defaultTest='test_attack.py')
