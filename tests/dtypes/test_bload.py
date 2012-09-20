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
        self.loadbuffer = BytesIO(b'\xfd\x99\x99\x00\x00\x00\x10' + self.content)
        self.new_loadbuffer = BytesIO(b'\x00\x00\x00\x00\x00\x00\x00' + self.content)

    def tearDown (self):
        del self.savebuffer
        del self.loadbuffer

    def testBSave(self):
        "bsave() creates correct data"
        bsave(self.content, self.savebuffer)
        ok(self.savebuffer.getvalue()) == (b'\xfd\x99\x99\x00\x00\x00\x10' + self.content)

    def testBSaveArray(self):
        "bsave(array) produces correct output"
        # note that the dtype doesn't matter here, except that
        # it must fit evenly into the length of self.content
        import numpy as np
        bsave(np.fromstring(self.content, dtype='B'), self.savebuffer)
        ok(self.savebuffer.getvalue()) == (b'\xfd\x99\x99\x00\x00\x00\x10' + self.content)

    def testBSaveNew(self):
        "bsave(newformat = True) creates correct data"
        bsave(self.content, self.savebuffer, newformat=True)
        ok(self.savebuffer.getvalue()) == (b'\x00\x00\x00\x00\x00\x00\x00' + self.content)

    def testBSaveArrayNew(self):
        "bsave(array, newformat = True) produces correct output"
        # note that the dtype doesn't matter here, except that
        # it must fit evenly into the length of self.content
        import numpy as np
        bsave(np.fromstring(self.content, dtype='B'), self.savebuffer, newformat=True)
        ok(self.savebuffer.getvalue()) == (b'\x00\x00\x00\x00\x00\x00\x00' + self.content)

    def testBSaveBigdataError(self):
        "bsave() raises ValueError when data size > 65535 bytes IFF not newformat"
        ok(lambda: bsave(b'B' * 72000, self.savebuffer)).raises(ValueError)
        ok(lambda: bsave(b'B' * 72000, self.savebuffer, newformat=True)).not_raise(ValueError)

    def testBLoad(self):
        "bload() returns correct data"
        ok(bload(self.loadbuffer)) == self.content

    def testBLoadBadMagic(self):
        "bload() raises ValueError when magic is wrong, IFF not newformat_ok"
        tmp = BytesIO(b'\xf2\x99\x99\x00\x00\x00\x10' + self.content)
        ok(lambda: bload(tmp)).raises(ValueError)
        ok(lambda: bload(tmp, newformat_ok=True)).not_raise(ValueError)

    def testBLoadAutosizing(self):
        "bload(...,newformat_ok=True) determines content size from file"
        tmp = BytesIO(b'\xfd\x99\x99\x00\x00\x00\x02' + self.content)
        ok(bload(tmp, newformat_ok=True)) == self.content

    def testBLoadLengthMismatch(self):
        "bload() raises ValueError when the amount of data is insufficient, but not if there is surplus"
        tmp = BytesIO(b'\xfd\x99\x99\x00\x00\x00\x20' + self.content)
        ok(lambda: bload(tmp)).raises(ValueError)
        # NOTE: having extra bytes on the end is actually valid, so
        # we test that it -succeeds-!
        tmp = BytesIO(b'\xfd\x99\x99\x00\x00\x00\x08' + self.content)
        ok(lambda: bload(tmp)).not_raise(ValueError)


if __name__ == "__main__":
    nose.main(defaultTest='test_bload.py')