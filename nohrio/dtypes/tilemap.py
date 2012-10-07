from nohrio.iohelpers import IOHandler, Filelike
from nohrio.dtypes.bload import BLOAD_SIZE
from nohrio.dtypes.common import readint, writeint
from collections import defaultdict, namedtuple
from bits import AttrStore, UnwrappingArray
from bits.dtype import DType
from bits.enum import Enum, MultiRange
from numpy import dtype
from struct import unpack, pack
import numpy as np

class TilemapBase(IOHandler, np.ndarray):
    __array_priority__ = 100
    def __new__ (cls, source, *args, maxlayers = 1,**kwargs):
        self = None
        if type(source) in {tuple, list}:
            self = np.zeros(source,'B')
        elif isinstance(source, np.ndarray):
            if source.dtype.kind != 'u':
                raise ValueError('Elements must be of unsigned integer type, not %r' % source.dtype)
            if source.ndim > 3:
                raise ValueError('%d-d tilemaps not supported.' % source.ndim)
            elif source.ndim < 2:
                raise ValueError('tilemaps must be at least 2-d, not %d-d.' % source.ndim)
            self = np.asarray(source)
        else:
            with Filelike(source, 'rb') as fh:
                # skip bload header -- we can't do this the nice way.
                # NOTE: this means we don't currently load very old maps correctly --
                # see http://rpg.hamsterrepublic.com/ohrrpgce/T
                fh.seek(BLOAD_SIZE)
                #print ('FH', fh)
                tmp = fh.read(4)
                #print ('tmp', tmp)
                w, h = unpack ('<2h', tmp)
                print (w,h)
                layer_nbytes = h * w
                layerindex = 0
                layerdata = []
                while layerindex < maxlayers:
                    data = fh.read(layer_nbytes)
                    if len(data) > 0 and len(data) < layer_nbytes:
                        raise IOError('Incomplete tilemap layer detected.'
                                      ' Read %d bytes,'
                                      ' expecting %d.' % (len(data),
                                                          layer_nbytes))
                    if data:
                        layerdata.append(data)
                    layerindex += 1
                print ('data len: %d, w,h = %d,%d' % (sum(len(l) for l in layerdata), w, h))
                self = np.fromstring(b''.join(layerdata),'B').reshape((-1, h, w))
        return self.view(cls)
    def __str__(self):
        return '%s<w=%d, h=%d, layers=%d, hash=0x%x>' % (self.__class__.__name__,
                                                         self.width,
                                                         self.height,
                                                         self.nlayers,
                                                         hash(self.data))
    def _save(self, fh):
        fh.write(b'\x00' * BLOAD_SIZE)
        fh.write(pack('<2h', self.width, self.height))
        fh.write(self.tostring())

    width = property(lambda self: self.shape[-1])
    height = property(lambda self: self.shape[-2])
    nlayers = property(lambda self: 1 if len(self.shape) == 2 else self.shape[-3])

class Tilemap(TilemapBase):
    def __new__(cls, *args, **kwargs):
        return TilemapBase.__new__(cls, *args, maxlayers=8, **kwargs)

class Foemap(TilemapBase):
    def __new__(cls, *args, **kwargs):
        self = TilemapBase.__new__(cls, *args, maxlayers=1, **kwargs)
        self.shape = self.shape[1:]
        return self


class Wallmap(TilemapBase):
    NORTH, EAST, SOUTH, WEST = 1, 2, 3, 4
    VEHA, VEHB, HARM, OVERHEAD = 5, 6, 7, 8
    def __new__(cls, *args, **kwargs):
        self = TilemapBase.__new__(cls, *args, maxlayers=1, **kwargs)
        self.shape = self.shape[1:]
        return self

WALL_NORTH, WALL_EAST, WALL_SOUTH, WALL_EAST = (Wallmap.NORTH, Wallmap.EAST,
                                                Wallmap.SOUTH, Wallmap.WEST)
WALL_VEHA, WALL_VEHB, WALL_HARM, WALL_OVERHEAD = (Wallmap.VEHA, Wallmap.VEHB,
                                                  Wallmap.HARM, Wallmap.OVERHEAD)

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
        w,h = None, None
        toplevel = RELOAD(source)['zonemap']
        w, h = toplevel['w','h']
        self.w = w
        self.h = h
        names = {}
        extradata = {}
        zones = toplevel['zones']
        for zone in zone.iter('zone'):
            thiszone = zone.value
            name = zone.get('name?') or ''
            extra = [0,0,0]
            for extraitem in zone.iter('extra?'):
                extra[extraitem.value] = extraitem['int']
            names[thiszone] = name
            extradata[thiszone] = tuple(extra)
        self.name = names
        self.extradata = extradata
        rows = {}
        _rows = toplevel['rows']
        for y in _rows.iter('y'):
            thisrow = {}
            for zone in y.iter('zone'):
                thisrow[zone.value] = zone['spans']
            rows[y.value] = tuple(thisrow)
        self.map = rows

    def _save(self, fh):
        writer = RELOADWriter(fh)
        zm = writer.sub('zonemap')
        zm['w','h'] = self.w, self.h
        zi = zm.sub('zones')
        for zone, info in self.info.items():
            thiszone = zi.sub('zone', zone)
            thiszone['name'] = info[0]
            for i, extra in enumerate(info[1]):
                with thiszone.sub('extra', i) as x:
                    x['int'] = extra
            thiszone.close()
        zi.close()
        with zm.sub('rows') as rows:
            for yvalue in sorted(self.map.keys()):
                y = rows.sub('y', yvalue)
                for zoneindex in sorted(self.map[yvalue].keys()):
                    zone = y.sub('zone', zoneindex)
                    zone['spans'] = self[map][yvalue][zone]
                    zone.close()
                y.close()
        zm.close()
        writer.close()

TAP_END = 0
TAP_UP, TAP_DOWN, TAP_RIGHT, TAP_LEFT = 1, 2, 3, 4
TAP_WAIT, TAP_CHECK = 5, 6
TAP_MAX = 6
MAX_TAP_COMMANDS = 9

TAPCommand = namedtuple('TAPCommand','op param')

class TileAnimationPattern(IOHandler,AttrStore):
    """Single tile-animation-pattern. There are two per map.

    """
    def __init__(self, source=None, starttile=0, disableif=0, code=None):
        if not source:
            if not code:
                code= [TAPCommand(TAP_END, 0),] * MAX_TAP_COMMANDS
        else:
            with Filelike(source, 'rb') as fh:
                starttile, disableif = readint(fh, n=2)
                actions = readint(fh, n=MAX_TAP_COMMANDS)
                params = readint(fh, n=MAX_TAP_COMMANDS)
                code = [TAPCommand(a, p) for a, p in zip(actions, params)]
        self.starttile = starttile
        self.disableif = disableif
        self.code = code

    def __getitem__(self, k):
        return self.code[k]

    def __setitem__(self, k, v):
        if type(v) != TAPCommand:
            raise ValueError('Cannot set TAP code from object of type %r' % type(v))
        if v.op > TAP_MAX:
            raise ValueError('Unknown TAP operation %d' % v.op)
        if not (-32768 < v.param < 32767):
            raise ValueError('TAP parameter value %d exceeds storable value range -32768..+32767' % v.param)
        self.code[k] = v

    def _save(self, fh):
        writeint(fh, self.starttile, self.disableif)
        actions = []
        params = []
        for a, p in self:
            actions.append(a)
            params.append(p)
        while len(actions) < MAX_TAP_COMMANDS:
            actions.append(TAP_END)
            params.append(0)
        writeint(fh, *(actions + params))




def in_zonemap(self, zoneindex, x, y):
    if y not in self.map or zoneindex not in self.map[y]:
        return False
    thisrow = self.map[y][zoneindex]
    on=True  # first run will be False
    cx=0
    for length in thisrow:
        if cx > x:
            break
        cx += length
        on = not on
    return on

def encodezonemapline(line):
    b = bytearray(0 for v in range(64))
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

def invalidzonemap(width, line):
    """Return True if the decoded data of `line` is the wrong length."""
    return sum(line) != width


if __name__ == "__main__":
    t = TileAnimationPattern('../../ohrrpgce/vikings/vikings.rpgdir/viking.tap')
    print(t)
