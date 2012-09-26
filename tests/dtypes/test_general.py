#!/usr/bin/env python3
#coding=utf8

from unittest import TestCase
import nose
import functools
from oktest import ok
import nohrio.nohrio2 as nohrio
import os
from nohrio.iohelpers import FilelikeLump
from bits import showbitsets

from nohrio.dtypes.general import GeneralData, _BITSETS

# test that all is where it should be in the gen data type.
# some fixed data strings go here
# from vikings, wander, etc.


def setgenversions(dest, pwdver = 257, rpgver = 17):
    import struct
    from nohrio.dtypes.bload import BLOAD_SIZE
    pwdversion = struct.pack('<h', pwdver)
    rpgversion = struct.pack('<h', rpgver)
    dest[BLOAD_SIZE+190] = rpgversion[0]
    dest[BLOAD_SIZE+191] = rpgversion[1]
    dest[BLOAD_SIZE+10] = pwdversion[0]
    dest[BLOAD_SIZE+11] = pwdversion[1]

class TestGeneralData(TestCase):
    def setUp (self):
        self.gen = GeneralData(source='../ohrrpgce.rpgdir/ohrrpgce.gen')
        #self.rpg = nohrio.open_rpg ('../ohrrpgce.rpgdir', 'r')
        #self.gen = self.rpg.general # GEN is one of the lumps that's automatically loaded.

    def tearDown (self):
        pass
        #self.rpg.close()

    def testMissingVersions(self):
        """GeneralData() raises ValueError if input is correct size but one or both version fields are not set."""
        from io import BytesIO
        a = bytearray((0 for i in range(1007)))
        for pwdver, rpgver in ((0,17,), (257,0), (0,0)):
            print ('testing with %r %r' % (pwdver,rpgver))
            setgenversions(a, pwdver, rpgver)
            bio = BytesIO(a)
            ok(lambda :GeneralData(source=bio)).raises(ValueError)

    def testGoodVersions(self):
        """GeneralData() succeeds if input is 1007 bytes and both version fields are set."""
        from io import BytesIO
        a = bytearray((0 for i in range(1007)))
        setgenversions(a)
        bio = BytesIO(a)
        ok(lambda :GeneralData(source=bio)).not_raise(ValueError)

    def testBadSize(self):
        """GeneralData raises ValueError if input is not 1007 bytes"""
        from io import BytesIO
        for size in (0,100,1005,1008,1920):
            a = bytearray((0 for i in range(1008)))
            setgenversions(a)
            bio = BytesIO(a)
            ok(lambda :GeneralData(source=bio)).raises(ValueError)
        #ok(self.gen.nbytes) == 1000

    def testBitsets(self):
        """GeneralData saves/restores bitsets correctly"""
        from io import BytesIO
        bio = BytesIO()
        bitsets = self.gen.misc.bitsets
        showbitsets (bitsets, _BITSETS)
        print ('bitsets =', bitsets)
        self.gen.save(bio)
        bio2 = BytesIO(bio.getvalue())
        nextgen = GeneralData(bio2)
        newbitsets = nextgen.misc.bitsets
        #newbitsets.reverse()
        #print (newbitsets.bin)
        #print (len(newbitsets), len(_BITSETS))
        #newbitsets.byteswap()
        showbitsets (newbitsets, _BITSETS)
        print ('newbitsets =', newbitsets)
        #raise ValueError()
        ok(bitsets) == newbitsets

    def testPassword(self):
        """passinfo.set(pwd); passinfo.check(pwd) == True"""
        pwd = 'abcdefg'
        self.gen.passinfo.set(pwd)
        ok(self.gen.passinfo.check(pwd)) == True



if __name__ == "__main__":
    nose.main(defaultTest='test_general.py')
