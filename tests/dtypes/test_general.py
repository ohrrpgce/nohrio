#!/usr/bin/env python3
#coding=utf8

from unittest import TestCase
import nose
import functools
from oktest import ok
import nohrio.nohrio2 as nohrio
import os

# test that all is where it should be in the gen data type.
# some fixed data strings go here
# from vikings, wander, etc.

class TestGeneral(TestCase):
    def setUp (self):
        self.rpg = nohrio.open_rpg ('../ohrrpgce.rpgdir', 'r')
        self.gen = self.rpg.general # GEN is one of the lumps that's automatically loaded.
    
    def tearDown (self):
        self.rpg.close()
    
    def testSize(self):
        """Length in bytes == 1000"""
        ok(self.gen.nbytes) == 1000
        
    def testPassword(self):
        """Password data is consistent"""
        
        pass
    def testfoo(self):
        pass


if __name__ == "__main__":
    nose.main(defaultTest='test_general.py')
    