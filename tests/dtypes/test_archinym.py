#!/usr/bin/env python3
#coding=utf8

from unittest import TestCase
import nose
from oktest import ok, todo
import os
import io
from nohrio.dtypes.archinym import Archinym



class TestArchinym(TestCase):
    prefix = 'foo'
    creator='Bazifier v.1.2bar'
    def setUp (self):
        pass
    def tearDown (self):
        pass

    def testInit (self):
        """Create from args"""
        a = Archinym(prefix=self.prefix, creator=self.creator)
        ok(a.prefix) == self.prefix
        ok(a.creator) == self.creator

    def testFileInit (self):
        """Create from file"""
        a = Archinym(source='../../ohrrpgce/vikings/vikings.rpgdir/')
        ok(a.prefix) == 'viking'
        ok(a.creator) == 'OHRRPGCE Editor: serendipity 20060218'

if __name__ == "__main__":
    nose.main(defaultTest='test_archinym.py')
