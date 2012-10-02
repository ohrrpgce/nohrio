from unittest import TestCase
import nose
from oktest import ok
# XXX zonemap
from nohrio.dtypes.tilemap import Tilemap, Foemap, Wallmap
from io import BytesIO

class testTilemap(TestCase):
    lumpfname_template='../../ohrrpgce/vikings/vikings.rpgdir/viking.%s'
    def testLoadTmap(self):
        t = Tilemap(self.lumpfname_template % 't00')
        print(t)
        assert 0


if __name__ == "__main__":
    nose.main(defaultTest='test_tilemap.py')
