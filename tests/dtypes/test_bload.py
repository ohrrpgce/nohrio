#!/usr/bin/env python3
#coding=utf8

from unittest import TestCase
import nose
import functools
from oktest import ok
import nohrio.nohrio2 as nohrio
from nohrio.dtypes.bload import bload, bsave
import os
from io import BytesIO

class TestBload(TestCase):
    content = b'Sixteen bytes..!'
    def setUp (self):
        self.savebuffer = BytesIO()
        self.loadbuffer = BytesIO(b'\x7d\x99\x99\x00\x00\x00\x10' + self.content)
    
    def tearDown (self):
        del self.savebuffer
        del self.loadbuffer
    
    def testBSave(self):
        "bsave() creates correct data"
        bsave(self.content, self.savebuffer)
        self.savebuffer.getvalue() == (b'\x7d\x99\x99\x00\x00\x00\x10' + self.content)
    
    def testBSaveBigdataError(self):
        "bsave() raises ValueError when data size > 65535 bytes"
        ok(lambda: bsave(b'B' * 72000, self.savebuffer)).raises(ValueError)
    
    def testBLoad(self):
        "bload() returns correct data"
        ok(bload(self.loadbuffer)) == self.content
    def testBLoadBadMagic(self):
        "bload() raises ValueError when magic is wrong"
        tmp = BytesIO(b'\x72\x99\x99\x00\x00\x00\x10' + self.content)
        ok(lambda: bload(tmp)).raises(ValueError)
    def testBLoadLengthMismatch(self):
        "bload() raises ValueError when the amount of data is insufficient"
        tmp = BytesIO(b'\x7d\x99\x99\x00\x00\x00\x20' + self.content)
        ok(lambda: bload(tmp)).raises(ValueError)
        # NOTE: having extra bytes on the end is actually valid, so 
        # we test that it -succeeds-!
        tmp = BytesIO(b'\x7d\x99\x99\x00\x00\x00\x08' + self.content)
        ok(lambda: bload(tmp)).not_raise(ValueError)


if __name__ == "__main__":
    nose.main(defaultTest='test_bload.py')