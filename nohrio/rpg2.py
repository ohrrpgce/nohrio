from numpy import memmap
import numpy as np
from nohrio.lump import read_lumpheader, lumpname_ok, Passcode
import os
from nohrio.dtypes import GENERAL, dt
from nohrio.ohrrpgce import archiNym
from weakref import proxy, WeakValueDictionary
from struct import unpack

class md5Array (np.ndarray):
    def md5 (self):
        from hashlib import md5
        return md5(self.data).hexdigest()

class OhrData (memmap, md5Array):
    def __getattr__ (self, k):
        dt = memmap.__getattribute__ (self, 'dtype').names
        if dt and k in dt:
            return self[k]
        else:
            return memmap.__getattribute__ (self, k)
    def __setattr__ (self, k, v):
        dt = memmap.__getattribute__ (self, 'dtype').names
        if dt and k in dt:
            self[k] = v
        else:
            memmap.__setattr__ (self, k, v)
    def __hasattr__ (self, k):
        dt = memmap.__getattribute__ (self, 'dtype').names
        return (dt and k in dt)
    def fields (self):
        return self.dtype.names()

packed_image_guesses = {
    5120 : (8, 32, 40),
    578 :  (34, 34),
    1250:  (50, 50),
    3200:  (80, 80),
    1600:  (8, 20, 20),
    576:   (2, 24, 24),
    3750:  (3, 50, 50),
    2048:  (16, 16, 16),}

class AttackData(object):
    # virtualization of the awkward attack data format,
    # that needs "stapling together"
    # Returns a newly allocated BufferArray each time.
    # when that is deleted or flush()ed, the data gets rewritten to disk.
    pass

class PackedImageData (OhrData):
    def unpack (self, dest = None, shape = None, transpose = None):
        if not shape:
            if self.shape[-1] in packed_image_guesses:
                shape = packed_image_guesses[self.shape[-1]]
            else:
                shape = self.shape
        # convert 4bpp -> 8bpp
        part2 = self & 0xf
        part1 = (self & 0xf0) >> 4
        newshape = shape
        if not dest:
            unpacked = np.empty (shape = newshape, dtype = np.uint8)
        else:
            unpacked = dest
        unpacked.flat[0::2] = part1
        unpacked.flat[1::2] = part2
        # transpose dimensions appropriately.
        if transpose:
            if transpose == 'xy':
                transpose = list (range (unpacked.ndim))
                transpose [-2:] = [transpose[-1], transpose[-2]]
                unpacked = np.transpose (unpacked, transpose)
            else:
                unpacked = np.transpose (unpacked, transpose)
        return unpacked

def pack (src, dest = None, transpose = None):
    """Pack 8bpp image(s) with <=16 colors into a 4bpp image.

    Optionally transpose the output.
    """
    if transpose:
        if transpose == 'xy':
            transpose = list (range (src.ndim))
            transpose [-2:] = [transpose[-1], transpose[-2]]
            src = np.transpose (src, transpose)
        else:
            src = np.transpose (src, transpose)
    # check whether the input fits in this array...
    if src.shape[-1] % 2:
        raise ValueError ('width %d is not an even number of pixels.' % src.shape[-1])
    nsrcpixels = src.nbytes
    if dest:
        ndestpixels = dest.nbytes * 2
        if nsrcpixels != ndestpixels:
            raise ValueError (
              '%d byte unpacked image cannot be packed into a %d byte destination!' %
              (nsrcpixels, ndestpixels))
        if (src.shape[:-1] + (src.shape[-1] / 2)) != dest.shape:
            raise ValueError (
              '%d byte pitch doesn\'t fit exactly %d pixels' %
              (dest.shape[-1], src.shape[-1] / 2))
    else:
        dest = np.zeros (shape = src.shape[:-1] + (src.shape[-1] / 2,), dtype='B')
    if src.max() > 15:
        raise ValueError ('source image should only contain indices [0...15]')
    # Take two source pixels, pack them into one destination pixel
    res = dest
    #return
    part2 = src.flat[0::2] << 4
    part1 = src.flat[1::2]
    res.flat[:] = part1
    res.flat[:] |= part2
    return res
    #raise NotImplementedError('pack')
    # reverse the above transform

def map_filename (path, prefix, type, n):
    if n < 100:
        tmp = os.path.join (path, '%s.%s%02d' % (prefix, type, n))
    else:
        tmp = os.path.join (path, '%d.%s' % (n,type))
    return tmp

class Map (object):
    def __init__ (self, rpg, n):
        self.rpg = proxy (rpg)
        #self.filename = map_filename (path, prefix, type, n)
        self.n = n
        fname = self.filename % 't'
        w,h = self._read_header (fname)
        layers = (os.path.getsize (fname) - 11) // (w*h)
        self.shape = (layers, h, w)
        # sanity check tile-ish map elements
        for type in 'ep':
            w2, h2 = self._read_header (self.filename % type)
            if w2 != w or h2 != h:
                raise IOError ('map %d: (tile|wall|foe)maps are of mismatched dimensions!' % self.n)
        # and other elements:
        for type, length in (('n', 3007), ('l',3007),('d',2007)):
            actual_length = os.path.getsize (self.filename % type)
            if actual_length != length:
                raise IOError('map %d: %r lump of non-canonical size (%d, expected %d)' %\
                              (self.n, type, actual_length, length))
    def resize (self, layers, h, w, offset):
        raise NotImplementedError('resize')
    def _read_header (self, filename):
        f = open (filename, 'rb')
        f.read(7)
        result = struct.unpack ('H',f.read(4))
        if (result[0] * result[1]) % (os.path.getsize (fname) - 11) > 0:
            raise IOError ('map %d file size is not a multiple of W*H bytes' % self.n)
    def _get_tilemap (self):
        fname = self.filename % 't'
        w,h = self._read_header (fname)
        layers = (os.path.getsize (fname) - 11) // (w*h)
        self.shape = (layers, h, w)
        return rpg.data (fname, offset = 11, dtype = 'B', shape = self.shape)
        # return a memmap with dtype (layers, w, h)
    def _get_wallmap (self):
        fname = self.filename % 'p'
        w,h = self._read_header (fname)
        shape = (1, h, w)
        return rpg.data (fname, offset = 11, dtype = 'B', shape = shape)
    def _get_foemap (self):
        fname = self.filename % 'e'
        w,h = self._read_header (fname)
        shape = (1, h, w)
        return rpg.data (fname, offset = 11, dtype = 'B', shape = shape)

    def _get_doors (self):
        return rpg.data('dox', offset = 600*self.index)
    def _get_filename (self):
        return map_filename (self.rpg.path,
                             self.rpg.archinym.prefix,
                             '%s', self.n)

    filename = property (_get_doors)
    doors = property (_get_doors)
    tile = property (_get_tilemap)
    foe = property (_get_foemap)
    wall = property (_get_wallmap)
    # XXX NPC def
    # XXX NPC loc

class MapManager (object):
    def __init__ (self, rpg):
        self.rpg = proxy (rpg)
        self.refs = WeakValueDictionary()
    def add (self):
        raise NotImplementedError ('add map')
    def __contains__ (self, k):
        tmp = map_filename (self.rpg.path,
                             self.rpg.archinym.prefix,
                             't', k)
        return (tmp in self.rpg.manifest)
    def __delitem__ (self, k):
        if type(k) != int:
            raise ValueError ('%r is not a valid map id'
                              ' (not an integer)' % k)
        if k not in self:
            raise ValueError ('%r is not a valid map id'
                              ' (references a map which doesn\'t exist)' % k)
        raise NotImplementedError('delete map')

class RPGHandler (object):
    _lumpmetadata = {
       'gen' : (7,0), # offset, flags
    }
    def prepare (self):
        self.general = self.data ('gen')
        self.passcode = Passcode (self.general)

class RPGFile (object):
    def __init__ (self, filename, mode):
        f = open (filename, 'rb')
        # mapping, step 1: Detect all lumps.
        self._lump_map = {}
        filename = 'nothing'
        while filename:
            filename, offset, size = read_lumpheader (f)
            if filename:
                if not self.lumpname_ok (filename):
                    raise IOError ('corrupted or non canonical lump name %r' % filename)
                self._lump_map[filename] = (offset, size)
                f.seek (offset + size)
        # mapping, step 2: create corresponding objects for the lumps we know
        # Mapping, final step: catalogue all lumps we don't understand.
        # Init, step 1: read GEN
        # Init, step 2: decode password, creating Passcode object.
        passcode = Passcode (self.general)

class RPGDir (RPGHandler):
    def __init__ (self, path, mode):
        import glob
        filenames = glob.glob (os.path.join (path,'*') )
        # classify filenames into old-style: WANDER.XYZ
        # and new style: XYZ.ABC

        self.archinym = archiNym ([v for v in filenames if v.endswith('archinym.lmp')][0])
        self.manifest = filenames
        from weakref import WeakValueDictionary
        self.mmaps = {}
        self.mode = mode
        self.path = path
        self.prepare()

    def data (self, lump, n = None, dtype = None, offset = None, **kwargs):
        """Create a memmap pointing at a given kind of lump"""
        boffset, flags = self._lumpmetadata.get(lump, (0, 0))
        if dtype == None:
            dtype = dt.get (lump, None)
        if offset == None:
            offset = 0
        offset += boffset
        if flags != 0:
            raise NotImplementedError('flags')
        if n != None:
            raise NotImplementedError('subindexed lumps')
        if os.path.exists (lump):
            filename = lump
        else:
            if lump.startswith('.'):
                lump = lump [1:]
            filename = os.path.join(self.path, self.archinym.prefix + "." + lump)
            if not os.path.exists (filename):
                raise IOError ('lump %r not found' % filename)
        if filename in self.mmaps:
            if self.mmaps[filename].dtype == dtype:
                return self.mmaps[filename]
            del self.mmaps[filename]
            self.mmaps[filename] = OhrData (filename, mode = self.mode, dtype = dtype, offset = offset)
            return self.mmaps[filename]
        else:
            self.mmaps[filename] = OhrData (filename, mode = self.mode, dtype = dtype, offset = offset)
            return self.mmaps[filename]
    def lump_path (self, lump, n = None):
        if n:
            raise NotImplementedError()
        if len(lump) <= 4:
            filename = os.path.join (self.path, self.archinym.prefix + "." + lump)
        else:
            filename = os.path.join (self.path, lump)
        if filename in self.manifest:
            return filename

    def __getitem__ (self, k):
        n= None
        dtype = None
        offset = None
        if type(k) != str:
            print "tuple indexed!"
            l = len(k)
            if l > 1:
                n = l[1]
            if l > 2:
                dtype = l[2]
            if l > 3:
                offset = l[3]
            k = l[0]
        return self.data (k, n, dtype, offset)



def RPG (filename, mode = 'r', base = None, dir = False):
    if 'r' in mode:
        if os.path.isdir (filename):
            return RPGDir (filename, mode)
        return RPGFile (filename, mode)
    elif 'w' in mode:
        raise NotImplementedError('foo')
