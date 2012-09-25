#!/usr/bin/env python3
#coding=utf8

from unittest import TestCase
import nose
import functools
from oktest import ok
import nohrio.nohrio2 as nohrio
import os
from nohrio.iohelpers import Filelike
from nohrio.dtypes.sprites import OHRSprite
import numpy as np

def loadspritedata(source, rawshape, i):
    recordsize = np.prod(rawshape)
    with Filelike(source) as f:
        f.seek (i*recordsize, 2)
        data = f.read(recordsize)
    return OHRSprite(np.fromstring(data,'B').reshape(rawshape))


class TestSprites(TestCase):
    spr = OHRSprite([[0, 0xf, 0xf0, 0x08],
                 [0xf, 0xf0, 0x08, 0x80],
                 [0xf0, 0x08, 0x80, 0],
                 [0x08, 0x80, 0, 0xf]])
    #def setUp (self):

        #self.gen = GeneralData(source='../ohrrpgce.rpgdir/ohrrpgce.gen')
        #self.rpg = nohrio.open_rpg ('../ohrrpgce.rpgdir', 'r')
        #self.gen = self.rpg.general # GEN is one of the lumps that's automatically loaded.

    #def tearDown (self):
    #    pass
        #self.rpg.close()

    def testPackedDefault(self):
        """OHRSprite(...) is set as packed by default"""
        ok(self.spr.packed) == True

    def testUnpack(self):
        """Unpacking"""
        unpacked = self.spr.unpack()
        ok(bytes(unpacked.data)) == (b'\x00\x00\x0f\x00\x00\x0f\x08\x00'
                                    b'\x0f\x00\x00\x0f\x08\x00\x00\x08'
                                    b'\x00\x0f\x08\x00\x00\x08\x00\x00'
                                    b'\x08\x00\x00\x08\x00\x00\x0f\x00')
        ok(unpacked.nframes) == self.spr.nframes
        ok(unpacked.shape[-1]) == self.spr.shape[-1] * 2
    def testRepack(self):
        """spr.unpack().pack() == spr"""
        ok(self.spr.unpack().pack()) == self.spr

    def testDoubleUnpack(self):
        """Unpacking a sprite that's already unpacked raises TypeError"""
        ok(lambda :self.spr.unpack().unpack()).raises(TypeError)

    def testDoublePack(self):
        """Packing a sprite that's already packed raises TypeError"""
        ok(lambda :self.spr.pack().pack()).raises(TypeError)

    def testNEQNonOHRSprite(self):
        """Compares non-equal with non-OHRSprite"""
        ok(self.spr) != np.asarray([[0, 0xf, 0xf0, 0x08],
                 [0xf, 0xf0, 0x08, 0x80],
                 [0xf0, 0x08, 0x80, 0],
                 [0x08, 0x80, 0, 0xf]])

if __name__ == "__main__":
    nose.main(defaultTest='test_sprites.py')
