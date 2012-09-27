from nohrio.iohelpers import IOHandler, Filelike
from collections import defaultdict
from bits import AttrStore, UnwrappingArray
from bits.dtype import DType
from bits.enum import Enum, MultiRange
from numpy import dtype
from struct import unpack
import numpy as np

class TilemapBase(IOHandler, np.ndarray):
    __array_priority__ = 100
    def __new__ (cls, source, *args, maxlayers = 1,**kwargs):
        self = None
        if type(source) in (tuple, list):
            self = np.zeros(source,'B')
        elif isinstance(source, np.ndarray):
            if source.dtype.kind != 'u':
                raise ValueError('Elements must be of unsigned integer type, not %r' % source.dtype)
            if source.ndim > 3:
                raise ValueError('%d-d tilemaps not supported.' % source.ndim)
            elif source.ndim < 2:
                raise ValueError('tilemaps must be at least 2-d, not %d-d.' % source.ndim)
            self = np.asarray(source).view(cls)
        else:
            with FileLike(source) as fh:
                w, h = unpack ('<2h', fh.read(4))
                layer_nbytes = h * w
                layerindex = 0
                while layerindex < maxlayers:
                    data = f.read(layer_nbytes)
                    if len(data) > 0 and len(data) < layer_nbytes:
                        raise IOError('Incomplete tilemap layer detected.'
                                      ' Read %d bytes,'
                                      ' expecting %d.' % (len(data),
                                                          layer_nbytes))
                    if data:
                        layerdata.append(data)
                    layerindex += 1
                self = np.fromstring(b''.join(layerdata),'B').reshape((-1, h, w))
        return self
    def __str__(self):
        return '%s<w=%d, h=%d, layers=%d, hash=0x%x>' % (self.__class__.__name__,
                                                         self.w,
                                                         self.h,
                                                         self.nlayers,
                                                         hash(self.data))

class Tilemap(TilemapBase):
    def __new__(cls, *args, **kwargs):
        return TilemapBase.__new__(cls, *args, maxlayers=8, **kwargs)

class Foemap(TilemapBase):
    pass

class Wallmap(TilemapBase):
    pass

# zm: 5 250 5
# x: 100
#
# 5: not break, off
# 250: break,on
#
# -> True
#
# x:255
# 5: not break, off
# 250: not break,on
# 5: break, off
#
# -> False


class Zonemap(IOHandler):
    def __init__(self, source):
        pass

def in_zonemap(self, zoneindex, x, y):
    if zoneindex not in self.zones:
        return False
    thiszone = self.zones[zoneindex]
    if y not in thiszone:
        return False
    thisrow = thiszone[y]
    on=True  # first run will be False
    cx=0
    for length in thisrow:
        if cx > x:
            break
        cx += length
        on = not on
    return on

def encodezonemapline(line):
    b = bytearray(0 for 0 in range(64))
    index = 0
    inputindex = 0
    inputlen = len(line)
    if line[0]: # starting 'in' the zone
        b[index] = 0
        index+=1
    while inputindex != inputlen:
        thisrun = 0
        curval = line[inputindex]
        while line[inputindex] == curval:
            thisrun += 1
            inputindex += 1
        while thisrun > 0:
            b[index] = min(thisrun, 255)
            index += 1
            thisrun -= 255
            # encode a run of >255 tiles
            if thisrun > 0:
                b[index] = 0
                index+= 1
    return b

def packzonemap(lines):
    """Pack encoded zonemap lines into a single bytearray.
       return a dictionary mapping { ycoord : (datastart,datalen)} and the bytearray.
       """
    totalsize = sum(len(v) for v in lines.values())
    dest = bytearray(0 for v in range(totalsize))
    index = {}
    order = lines.keys()
    order.sort()
    start = 0
    for k in order:
        line = lines[k]
        length = len(line)
        dest[start:start + length] = line
        index[k] = (start, length)
        start += length
    return index, dest


