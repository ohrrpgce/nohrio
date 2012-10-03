from collections import namedtuple
from bits import Enum, MultiRange, AttrStore, readmany, writemany
from bits.dtype import DType
from nohrio.dtypes.common import (INT16_MAX, scalararray, copyfrom, readint)
from nohrio.dtypes.bload import BLOAD_SIZE, bload, bsave
from nohrio.iohelpers import IOHandler, Filelike
import numpy as np


class MasterPalette(IOHandler, np.ndarray):
    """RGB(A) master palette.

    Stored in-memory with an alpha channel for easy application.
    """
    def __new__(cls, *args, source=None, newformat=False, count=1, **kwargs):
        if source:
            with Filelike(source, 'rb') as fh:

                if newformat:
                    # header is handled by caller, since
                    # multiple palettes can exist.
                    tmp = fh.read(256 * 3 * count)
                    if count > 0 and len(tmp) != (256 * 3 * count):
                        raise ValueError('Not enough data'
                                         ' (%d instead of %d)' % (len(tmp),
                                                                  (256 * 3 * count)))
                    loaded = np.fromstring(tmp, dtype='B')
                else:
                    tmp = bload(fh)
                    if len(tmp) != (256 * 3 * 2):
                        print (fh.tell())
                        raise ValueError('Not enough data'
                                         ' (%d instead of %d)' % (len(tmp),
                                                                  (256 * 3 * 2)))
                    loaded = np.fromstring(tmp, dtype='h')
                    loaded = loaded.astype('B')
                print ('LS', loaded.shape)
                loaded.shape = (-1, 256, 3)
                new = np.empty(shape = loaded.shape[:-1] + (4,),
                               dtype = loaded.dtype)
                new[...,:3] = loaded
                new[:,1:,3] = 255  # fixed alpha channel
                new[:,0,3] = 0
                if count > 0 and count != loaded.shape[0]:
                    raise ValueError('Expected %d master'
                                     ' palettes, got %d' % (count,
                                                            loaded.shape[0]))
                elif count == 1:
                    new.shape = (256, 4)
                return new.view(cls)
        return np.ndarray.__new__(cls, *args, **kwargs)

    def apply(self, item):
        """Apply single master palette to a indexed-palette or sprite.

        (Convert indices to RGBA pixels)"""
        return item.take(self, axis=-2)


    def _save(self, fh, newformat=False):
        if not newformat:
            if self.ndims > 2:
                raise ValueError('Can\'t save multiple (%d) master palettes in old format' % self.shape[0])
            self = self.astype('h')
            bsave(self.data, fh)
            return
        self = self[...,:3]
        fh.write(self.tostring())


class SpritePalette(IOHandler, np.ndarray):

    def __new__(cls, *args, source=None, count=1, **kwargs):
        if source:
            with Filelike(source, 'rb') as fh:
                tmp = np.fromstring(fh.read(16*count),
                                    dtype='B').reshape((count, 16)).view(cls)
                if count == 1:
                    tmp.shape = (16,)
                return tmp
        return __new__(cls, *args, **kwargs)

    def _save(self, fh):
        fh.write(self.tostring())

    def apply(self, sprite, masterpalette):
        """Convert an 8bit indexed sprite to 32bit rgba by applying the palette.

        :Parameters:
            sprite: OHRSprite
                Must be unpacked and linear.
        """
        cls = sprite.__class__
        return masterpalette.apply(sprite.take(self)).view(cls)


def loadallpalettes(rpg):
    """Examine the rpg and load all master and sprite palettes.

    :Returns:
        masterpalettes: MasterPalette instance
            of shape (NMASTERPALETTES, 256, 3)
        spritepalettes: SpritePalette instance
            of shape (NSPRITEPALETTES, 16)
    """
    master, sprite = None, None
    print({k:v for k,v in rpg.index.items() if 'mas' in k or 'pal' in k})
    print ([v in rpg for v in ('mas', 'palettes.bin')])
    if 'mas' in rpg and 'palettes.bin' not in rpg:
        with rpg.openlump('mas', 'rb') as fh:
            master = MasterPalette(source=fh)
    else:
        with rpg.openlump('palettes.bin', 'rb') as fh:
            hdrsize, palettesize = readint(fh, 2)
            if hdrsize != 4:
                print ('WARNING: remainder of master palette header'
                       'was not loaded (%d bytes of unknown data)' % (hdrsize - 4))
                fh.seek(hdrsize, 0)
            if palettesize != (256 * 3):
                raise ValueError('Only 256-color 8bpc RGB palettes'
                                 ' are supported.'
                                 ' (found palsize=%d,'
                                 ' expecting 768)' % palettesize)
            master = MasterPalette(source=fh, newformat=True, count=-1)
    with rpg.openlump('pal', 'rb') as fh:
        magic = readint(fh)
        if magic != 4444:
            fh.seek(0, 0)
            sprite = np.fromstring(bload(fh), dtype='B')
            sprite.shape = (-1, 16)
            sprite = sprite.view(SpritePalette)
        else:
            maxpal = readint(fh)
            __reserved = readint(fh,6)
            sprite = SpritePalette(source=fh, count=maxpal + 1)
    return master, sprite


if __name__ == "__main__":
    with Filelike('../../ohrrpgce/vikings/vikings.rpgdir/viking.pal', 'rb') as fh:
        fh.seek(16*10)
        pal = SpritePalette(source=fh)
        assert ((pal == [  0, 145,  49, 147,  52, 150, 248,
                           7, 153,  54, 252, 253, 240, 159, 218,  15]).all())
    with Filelike('../../ohrrpgce/vikings/vikings.rpgdir/palettes.bin', 'rb') as fh:
        fh.seek(4)
        maspal = MasterPalette(source=fh, newformat=True)
        print(maspal)
        f2 = open('/tmp/palbin','wb')
        f2.write(b'\x04\x00\x00\x03')
        maspal.save(f2, newformat=True)
        f2.close()