#!/usr/bin/env python3
#coding=utf8
from unittest import TestCase
import nose
import functools
from oktest import ok
from nohrio.iohelpers import IOHandler, dtype2struct
import os
import numpy as np
import struct

f = open ('/tmp/nohriohandlers.test','wb')
f.write(np.random.bytes(64))
f.close()
del f

class SingletonRecord(IOHandler, np.ndarray):
    def __init__ (self, *args, **kwargs):
        origin = kwargs.get('origin', None)

    def _save (self, fh):
        fh.write(self.tostring())
    def _load (self, fh):
        tmp = self.fh.read()


class TestIOHandler(TestCase):
    def setUp (self):
        pass

    def tearDown (self):
        pass

    def testDtype2Struct(self):
        """dtype2struct(dt) succeeds for all standard non-structured dtypes"""
        def compile (dt):
            dtype2struct(dt, can_simplify = True)
        for endianness in "<>":
            for item in '?bhilqpBHILQPefdSMm':
                thisdt = np.dtype(endianness + item)
                ok(lambda: compile(thisdt)).not_raise(Exception)

    def testDtype2StructFail(self):
        """dtype2struct(dt) fails for non-standard non-structured dtypes"""
        def compile (dt):
            dtype2struct(dt, can_simplify = True)
        for endianness in "<>":
            for item in 'gFDGUVO':
                thisdt = np.dtype(endianness + item)
                ok(lambda: compile(thisdt)).raises(ValueError)

    def testDtype2StructFailND(self):
        """dtype2struct(dt) fails for dtypes where len(shape) > 1"""
        import random
        def r16():
            return random.randint(1,16)
        def compile (dt):
            dtype2struct(dt, can_simplify = True)
        for endianness in "<>":
            for item in '?bhilqpBHILQPefdSMm':

                thisdt = np.dtype(endianness + ('(%d,%d)' % (r16(), r16())) + item,)
                ok(lambda: compile(thisdt)).raises(ValueError)
    def testDtype2Struct1D(self):
        """dtype2struct(dt) succeeds for dtypes where len(shape) == 1"""
        # XXX select dtypes randomly -- but not object, datetime, timedelta, or string
        #     from the numpy list of dtypes.

        import random
        def r16():
            return random.randint(1,16)
        def compile (dt):
            dtype2struct(dt, can_simplify = True)
        for endianness in "<>":
            for item in '?bhilqpBHILQPefdSMm':
                thisdt = np.dtype(endianness + ('%d' % r16()) + item,)
                ok(lambda: compile(thisdt)).not_raise(Exception)

    def testDtype2StructComplex(self):
        """dtype2struct(dt) succeeds for dtypes made exclusively of struct-compatible types"""
        def compile (dt):
            dtype2struct(dt, can_simplify = True)
        for endianness in "<>":
            for item in ('B,B,B', 'H,H', 'h,4h'):
                dt = np.dtype(item)
                thisdt = np.dtype(endianness + item)
                ok(lambda: compile(thisdt)).raises(ValueError)


if __name__ == "__main__":
    nose.main(defaultTest='test_2iohelpers.py')
