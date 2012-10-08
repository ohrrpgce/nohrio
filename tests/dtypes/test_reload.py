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

class testReadReload(TestCase):
    def testOpen(self):
        """Open simple document"""
        assert 0

    def testSingleAccess(self):
        """[existing_name] -> ReadNode"""
        assert 0

    def testNoexistAccess(self):
        """[nonexisting_name] raises KeyError """
        assert 0

    def testMultiaccessLen(self):
        """[multiple, existing, keys] -> seq of ReadNode, len() == nkeys"""
        assert 0

    def testMultinoexistAccess(self):
        """[multiple, keys, some, not, present] raises KeyError"""
        assert 0

    def testSub(self):
        """.sub(name) -> ReadNode(name = name)"""
        assert 0

    def testSubExistVal(self):
        """.sub(name, existing_value) -> ReadNode(value = existing_value)"""
        assert 0

    def testSubNoexistVal(self):
        """.sub(name, nonexisting_value) raises ValueError """
        assert 0

    def testNoexistSub(self):
        """.sub(nonexisting_name) raises KeyError"""
        assert 0

    def testStr(self):
        """.str() -> str if type(self) == bytes"""
        assert 0

    def testNonStr(self):
        """.str() raises TypeError if type(self) != bytes"""
        assert 0

    def testIter(self):
        """.iter() returns a sequence of ReadNodes w/ appropriate names"""
        assert 0

    def testIterVal(self):
        """.iter(..,val) returns a sequence of ReadNodes w/ appropriate names and values"""
        assert 0

    def testIterPred(self):
        """.iter(..,pred) returns a sequence of ReadNodes w/ appropriate names and values"""
        assert 0

    def testPathKey(self):
        """[path] looks up nested nodes correctly"""
        assert 0

    def testPath(self):
        """.path returns a usable node path"""
        assert 0

    def testIndices(self):
        """.indices returns a usable indices tuple"""
        assert 0

    def testContains(self):
        """`name in self` works """
        assert 0

    def testCount(self):
        """.count(name) -> correct count """
        assert 0

    def testEqual(self):
        """== othernode compares accurately, ignoring node order"""
        assert 0

    def testIgnored(self):
        """.ignored returns an accurate list"""
        assert 0


class testWriteReload(TestCase):
    def testRWCycle(self):
        """read(read().write()) == original"""
        assert 0

    def testSub(self):
        """sub(name) adds new child"""
        assert 0

    def testKeyAdd(self):
        """[name] = v adds new child"""
        assert 0

    def testKeyOverwriteFails(self):
        """[existing_name] = v raises KeyError"""
        assert 0

    def testKeyMultiAdd(self):
        """[multinames] = multivals adds children"""
        assert 0

    def testKeyMultiOverwriteFails(self):
        """[some_existing_names] = multivals raises KeyError"""
        assert 0

    def testAddExisting(self):
        """Add(existing_name, value) adds new child"""
        assert 0

    def testKeyAddMultiWronglenFails(self):
        """[multinames] = wronglen_vals raises ValueError"""
        assert 0

    def testDelExisting(self):
        """Del [existing_name] removes exactly 1 child"""
        assert 0

    def testDelNonexisting(self):
        """Del [nonexisting_name] raises KeyError"""
        assert 0

    def testDelMultiExisting(self):
        """Del [multi_existing_names] removes exactly 1 of each"""
        assert 0

    def testSave(self):
        """Save(fh) produces expected data"""
        assert 0

    def testSaveWOChildren(self):
        """Save(fh, children=False) produces data minus child nodes"""
        assert 0

    def testAssignChildren(self):
        """.children = iterable ok"""
        assert 0

    def testBadAssignChildren(self):
        """.children = non-iterable raises TypeError"""
        assert 0

    def testIndices(self):
        """.indices raises TypeError"""
        ok(lambda:WriteNode('foo').indices).raises(TypeError)

if __name__ == "__main__":
    nose.main(defaultTest='test_reload.py')
