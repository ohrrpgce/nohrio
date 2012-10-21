from unittest import TestCase
import nose
import functools
from oktest import ok
import nohrio.nohrio2 as nohrio
import os
from nohrio.iohelpers import FilelikeLump
from bits import showbitsets
from nohrio.dtypes.reload import RELOAD, ReadNode, WriteNode
from testutils import loadsaveok

class testReadReload(TestCase):
    def setup(self):
        self.rld = RELOAD(self.simple_testdata, 'r')
    def testOpen(self):
        """Open simple document"""

        root = tmp['root']
        ok([c.name for c in root.children]) == ['simple', 'nested']
        ok(root['simple']) == 42
        nested = root['nested']
        ok(type(nested)) == ReadNode
        ok(nested['count']) == 7
        ok(len(root.ignored_nodes())) == 0

    def testSingleAccess(self):
        """[existing_simple_node_name] -> simple type"""
        tmp = self.rld
        root = tmp['root']
        ok(type(root['simple'])) == 42

    def testNoexistAccess(self):
        """[nonexisting_name] raises KeyError """
        tmp = self.rld
        ok(lambda:tmp['fruit']).raises(KeyError)

    def testMultiaccessLen(self):
        """[multiple, existing, keys] -> seq of ReadNode, len() == nkeys"""
        assert 0

    def testMultinoexistAccess(self):
        """[multiple, keys, some, not, present] raises KeyError"""

        ok(lambda: tmp['root']['simple', 'nested', 'kamina']).raises(KeyError)

    def testSub(self):
        """.sub(name) -> ReadNode(name = name)"""
        tmp = self.rld
        ok(tmp.sub('root').__class__) == ReadNode

    def testSubExistVal(self):
        """.sub(name, existing_value) -> ReadNode(value = existing_value)"""
        tmp = self.rld
        root = tmp['root']
        ok(root.sub('simple', 42).value) == 42


    def testSubNoexistVal(self):
        """.sub(name, nonexisting_value) raises ValueError """
        tmp = self.rld
        root = tmp['root']
        ok(lambda:root.sub('simple', 24)).raises(ValueError)

    def testNoexistSub(self):
        """.sub(nonexisting_name) raises KeyError"""
        tmp = self.rld
        root = tmp['root']
        ok(lambda:root.sub('fruit')).raises(KeyError)

    def testStr(self):
        """.str() -> str if type(self) == bytes"""
        tmp = self.rld
        ok(type(tmp['root'].sub('bites').str())) == str

    def testNonStr(self):
        """.str() raises TypeError if type(self) != bytes"""
        tmp = self.rld
        ok(lambda:type(tmp['root'].sub('simple').str())).raises(TypeError)

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
        tmp = self.rld
        ok(tmp['root/nested/count']) == tmp['root']['nested']['count']

    def testPathRelError(self):
        """[relative_path] raises KeyError"""
        tmp = self.rld
        ok(lambda:tmp['root']['nested']['../nested/count']).raises(KeyError)

    def testPath(self):
        """.path returns a usable node path"""
        tmp = self.rld
        ok(tmp.sub('root').path) == 'root'
        ok(tmp['root'].sub('nested').path) == 'root/nested'
        ok(tmp['root']['nested'].sub('count').path) == 'root/nested/count'

    def testBlankPathItem(self):
        """.path returns a usable node path when blank-named nodes are in the path"""
        assert 0

    def testIndices(self):
        """.indices returns a usable indices tuple"""

        ok(root.sub('simple').indices) == (0, 0)
        ok(root['nested'].sub('count').indices) == (0, 1, 0)

    def testContains(self):
        """`name in self` works """
        tmp = self.rld
        ok(lambda v:'root' in tmp) == True
        ok(lambda v:'simple' in tmp) == False
        ok(lambda v:'simple' in tmp['root']) == True
        ok(lambda v:'nested' in tmp['root']) == True
        ok(lambda v:'count' in tmp['root']['nested']) == True

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
