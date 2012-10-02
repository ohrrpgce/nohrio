from collections import namedtuple
import numpy as np
from bits import UnwrappingArray

_statlist = 'hp mp str acc def dog mag wil spd ctr foc xhits'.split()
stats = ''.join('h:%s:' % v for v in _statlist)
statranges = ''.join('2h:%s:' % v for v in _statlist)
spelllist = '24T{h:attack:h:level:}'

Coords = namedtuple('Coords', 'x y')
PalettedPic = namedtuple('PalettedPic', 'pic pal')
StatList = namedtuple('StatList', 'hp mp str acc defe dog mag wil spd ctr foc xhits')
MAX_ELEMENTS = 64

def readstr(fh, lengthbytes, characterbytes, maxchars):
    length = fh.read(lengthbytes)[0]
    print(repr(length))
    data = fh.read(maxchars * characterbytes)[::characterbytes]
    return ''.join(chr(c) for c in data[:length])

def writestr(fh, s, lengthbytes, characterbytes, maxchars):
    if type(s) != bytes:
        s = s.encode('utf8')
    slen = len(s)
    if slen > maxchars:
        raise ValueError('Can\'t fit %r into %d characters' % (s, slen))
    fh.write(bytes((slen,)))
    if lengthbytes > 1:
        fh.write(b'\x00' * (lengthbytes-1))
    contentbuffer = bytearray(0 for v in range(characterbytes*maxchars))
    contentbuffer[::characterbytes] = s
    fh.write(contentbuffer)

def scalararray(dtype, data=None):
    """Create a new scalar array of dtype, optionally initialized from data"""
    tmp = None
    if data:
        tmp = np.frombuffer(data, dtype)
    else:
        tmp = np.zeros((), dtype)
    return tmp.reshape(()).view(UnwrappingArray)

ALL=object()
PUBLIC=object()

def copyfrom(src, dest, skeys=None, sattrs=None, dkeys=None, dattrs=None):
    """Copy attributes and/or keyvalue pairs from one object to attributes or keys on another.

    :Parameters:
        src: object
            Source of attributes and/or keyvalue pairs
        dest: object
            Destination for keyvalue pairs or attributes
        skeys: seq of str, or ALL
            keys to copy.
            If ALL, keys are produced by iterating over src.
        sattrs: seq of str, or ALL
            attributes to copy.
            If ALL, attributes are produced by iterating over dir(src).
            If PUBLIC, similar, but items which begin with an underscore are ignored.
        dkeys: True or seq of str
            If True, copy to keys without renaming.
            else , dkeys must be a sequence of strings of len == (len(skeys) + len(sattrs))
        dattrs: True or seq of str
            If True, copy to attributes without renaming.
            else , dattrs must be a sequence of strings of len == (len(skeys) + len(sattrs))

    :Examples:
        uniformly typed data from file -> named attributes:
            >>> copyfrom(struct.unpack('<12h', f.read(24)), statbonuses,
                        'hp mp attack aim defense dodge magic will speed counter'
                        'mpreduction hits', dattrs=True)
        uniformly typed data from array -> named attributes:
            >>> copyfrom(arr[0], ALL, dattrs='src dest destmap tagcheck tagcheck2')

    """
    if not ((skeys or dkeys) or (sattrs or dattrs)):
        pass