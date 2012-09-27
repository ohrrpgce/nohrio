from nohrio.iohelpers import IOHandler
import numpy as np


def load(cls, fh):
    pass

class OHRSprite(IOHandler, np.ndarray):
    """Paletted sprite. May be packed (4bpp) or unpacked(8bpp).

       :Attributes:
            packed: bool
                True if the content is 4bpp packed (2 pixels/byte)
                along the last axis(y)
            nframes: int
                1 if self.ndim == 2, else self.shape[-1]
    """

    def __new__ (cls, *args, packed=True, origin=None, dtype='B', **kwargs):
        self = np.asarray(*args, dtype=dtype, **kwargs).view(cls)
        if self.ndims < 2:
            raise ValueError('OHRSprites can only be instantiated as a >= 2-d array')
        self.packed = packed
        self.origin = origin
        return self

    def __eq__ (self, y):
            if not isinstance(y, __class__):
                return False
            if self.packed != y.packed:
                return False
            return (self.view(np.ndarray) == y.view(np.ndarray)).all()

    __ne__ = lambda self,y: not self.__eq__(y)

    def pack(self):
        """Return a packed (8bpp -> 4bpp) version of the sprite.

        :Raises:
            TypeError: when sprite is already packed (```self.packed == True```)
            IndexError: when a palette index in the sprite exceeds 15.
        """
        if self.packed:
            raise TypeError('Already packed')
        maxvalue = self.max()
        if maxvalue > 15:
            raise IndexError('Images containing palette indices > 15'
                             ' cannot be packed into a 4bpp format.')
        # XXX stuff.
        #
        low = self.flat[::2]
        hi = self.flat[1::2] << 4
        newshape = self.shape[:-1] + (self.shape[-1] / 2,)
        instance = np.zeros(newshape, dtype='B').view(OHRSprite)
        instance.flat[:] = low
        instance.flat[:] |= hi
        instance.packed = True
        return instance

    def unpack(self):
        """Return an unpacked (4bpp -> 8bpp) version of the sprite.

        :Raises:
            ValueError: when sprite is not packed.
        """
        if not self.packed:
            raise TypeError('Already unpacked')
        low = self & 0xf
        hi = (self >> 4)
        newshape = self.shape[:-1] + (self.shape[-1] * 2,)
        instance = np.zeros(newshape, dtype='B').view(OHRSprite)
        instance.flat[::2] = low
        instance.flat[1::2] = hi
        instance.packed = False
        return instance

    def _nframes(self):
        if len(self.shape) > 2:
            return self.shape[-3]
        return 1

    nframes = property(_nframes, doc = "Number of frames in this spriteset.")

foo = OHRSprite([[0, 0xf, 0xf0, 0x08],
                 [0xf, 0xf0, 0x08, 0x80],
                 [0xf0, 0x08, 0x80, 0],
                 [0x08, 0x80, 0, 0xf]])
print (foo.packed)
print (foo.unpack().pack())