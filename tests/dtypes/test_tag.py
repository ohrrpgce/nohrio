#!/usr/bin/env python3
#coding=utf8

from unittest import TestCase
import nose
from oktest import ok
import os
import io
import nohrio.nohrio2 as nohrio
from nohrio.dtypes.tag import TagCheck



# XXX move this into a shared test resources module
def save_to_bytes(obj, *args, **kwargs):
    """Return the bytes generated by obj.save(bytesio, *args,**kwargs)"""
    output = io.BytesIO()
    obj.save(output, *args, **kwargs)
    return output.getvalue()

def load_from_bytes(cls, _bytes, *args, **kwargs):
    """Return the object generated by cls.load(bytesio, *args,**kwargs)"""
    input = io.BytesIO(_bytes)
    return cls.load(None, input, *args, **kwargs)

class TestTagCheck(TestCase):
    # XXX for now, we don't try to equip self to rpg properly.
    rpg = 'RPG'
    def setUp (self):
        pass
    def tearDown (self):
        pass

    def testConflictingParams (self):
        """TagCheck(>1 of value|on|off) raises ValueError"""
        ok(lambda: TagCheck(self.rpg, value = 1000, on = 1000)).raises(ValueError)
        ok(lambda: TagCheck(self.rpg, on = 1000, off = 1000)).raises(ValueError)
        ok(lambda: TagCheck(self.rpg, value = 1000, off = 1000)).raises(ValueError)
        ok(lambda: TagCheck(self.rpg, value = 1000, on = 1000, off = 1000)).raises(ValueError)

    def testValue (self):
        """TagCheck(value=x) == x"""
        ok(int(TagCheck(self.rpg, 1000))) == 1000

    def testOn (self):
        """TagCheck(on=x) == x"""
        ok(int(TagCheck(self.rpg, on = 1000))) == 1000

    def testOff(self):
        """TagCheck(off=x) == -x"""
        ok(int(TagCheck(self.rpg, off = 1000))) == -1000

    def testBadOnOff(self):
        """Negative values accepted for value and rejected(ValueError) for on|off"""
        ok(lambda: TagCheck(self.rpg, off = -1000)).raises(ValueError)
        ok(lambda: TagCheck(self.rpg, on = -1000)).raises(ValueError)
        ok(lambda: TagCheck(self.rpg, value = -1000)).not_raise(ValueError)

    def testDifferentTypes(self):
        """TagCheck(x) != int(x)"""
        # TagCheck incorporates extra data which means this comparison should fail
        ok(TagCheck(self.rpg, 1000)) != 1000

    def testBadCompare(self):
        """TagCheck(x) (<|<=|>|>=) int(x) raises TypeError"""
        ok(lambda: TagCheck(self.rpg, 1000) < 1001).raises(TypeError)
        ok(lambda: TagCheck(self.rpg, 1000) <= 1000).raises(TypeError)
        ok(lambda: TagCheck(self.rpg, 1000) > 999).raises(TypeError)
        ok(lambda: TagCheck(self.rpg, 1000) >= 1000).raises(TypeError)

    def testEqual (self):
        """TagCheck(x) == Tagcheck(x)"""
        ok(TagCheck(self.rpg, 1000)) == TagCheck(self.rpg, 1000)

    def testStr(self):
        """TagCheck() str() looks normal"""
        ok(str(TagCheck(self.rpg, 1000))) == "RPG.TagCheck(on = 1000)"
        ok(str(TagCheck(self.rpg, on = 1000))) == "RPG.TagCheck(on = 1000)"
        ok(str(TagCheck(self.rpg, off = 1000))) == "RPG.TagCheck(off = 1000)"
        ok(str(TagCheck(self.rpg, 0))) == "RPG.TagCheck(on = 0 (Never))"
        ok(str(TagCheck(self.rpg, 1))) == "RPG.TagCheck(on = 1 (Always))"

    def testRepr(self):
        """TagCheck() repr() looks normal"""
        ok(repr(TagCheck(self.rpg, 1000))) == "TagCheck('RPG', on = 1000)"
        ok(repr(TagCheck(self.rpg, on = 1000))) == "TagCheck('RPG', on = 1000)"
        ok(repr(TagCheck(self.rpg, off = 1000))) == "TagCheck('RPG', off = 1000)"
        ok(repr(TagCheck(self.rpg, 0))) == "TagCheck('RPG', on = 0)"
        ok(repr(TagCheck(self.rpg, 1))) == "TagCheck('RPG', on = 1)"

    def testSave(self):
        """TagCheck().save() outputs in correct binary format"""
        ok(save_to_bytes(TagCheck(self.rpg, 1000))) == b'\xe8\x03'
        ok(save_to_bytes(TagCheck(self.rpg, -1000))) == b'\x18\xfc'
        ok(save_to_bytes(TagCheck(self.rpg, 0))) == b'\x00\x00'

    def testLoad(self):
        """TagCheck.load() parses correct binary format appropriately"""
        # hack. I haven't decided how the class creator should be accessed yet
        cls = TagCheck(self.rpg, 0).__class__
        ok(load_from_bytes(cls, b'\xe8\x03')) == TagCheck(self.rpg, 1000)
        ok(load_from_bytes(cls, b'\x18\xfc')) == TagCheck(self.rpg, -1000)
        ok(load_from_bytes(cls, b'\x00\x00')) == TagCheck(self.rpg, 0)

if __name__ == "__main__":
    print (TagCheck('foo', 1000))
    nose.main(defaultTest='test_tag.py')
    