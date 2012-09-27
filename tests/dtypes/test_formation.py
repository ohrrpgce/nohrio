from unittest import TestCase
import nose
from oktest import ok
from nohrio.dtypes.formation import FormationData, FormationSetData
from bits import AttrStore
from io import BytesIO

class testFormation(TestCase):
    record = (b'%\x00\x00\x00@\x00\x00\x00&\x00P\x00@\x00\x00\x00'
             b'\x16\x00h\x00X\x00\x00\x00\x00\x00\x00\x00'
             b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
             b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
             b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
             b'\x00\x06\x00\x0c\x00\x00\x00\x00\x00\x00\x00'
             b'\x00\x00\x00\x00\x00\x00')
    expected_enemies = [AttrStore(y=64, x=0, type=37, unused=0),
                        AttrStore(y=64, x=80, type=38, unused=0),
                        AttrStore(y=88, x=104, type=22, unused=0),
                        AttrStore(y=0, x=0, type=0, unused=0),
                        AttrStore(y=0, x=0, type=0, unused=0),
                        AttrStore(y=0, x=0, type=0, unused=0),
                        AttrStore(y=0, x=0, type=0, unused=0),
                        AttrStore(y=0, x=0, type=0, unused=0)]
    expected_info = AttrStore(unused=[0, 0, 0, 0],
                              bg=6, music=12, bgspeed=0, bgframes=0)

    def testLoad(self):
        """Load predefined data -> expected values"""
        io = BytesIO(self.record)
        f = FormationData(io)
        ok(f.enemies) == self.expected_enemies
        ok(f.info) == self.expected_info

    def testSave(self):
        """Save predefined values -> expected record data"""
        io = BytesIO(self.record)
        f = FormationData(io)
        io = BytesIO()
        f.save(io)
        ok(io.getvalue()) == self.record

class testFormationSet(TestCase):
    fs = FormationSetData('../../ohrrpgce/vikings/vikings.rpgdir/viking.efs')
    def testLoad(self):
        ok(int(self.fs.tagcheck)) == 0
        ok(self.fs.unused) == [0, 0, 0]
        ok(self.fs.frequency) == 4
        ok(self.fs.entries) == [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 150, 138, 139, 140, 141, 142]
    def testSave(self):
        io = BytesIO()
        self.fs.save(io)
        io2 = BytesIO(io.getvalue())
        fs2 = FormationSetData(io2)
        ok(self.fs) == fs2

if __name__ == "__main__":
    nose.main(defaultTest='test_formation.py')
