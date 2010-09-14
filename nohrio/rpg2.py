from numpy import memmap
import numpy as np
from nohrio.lump import read_lumpheader, lumpname_ok, Passcode
import os
from nohrio.dtypes import GENERAL, dt
from nohrio.ohrrpgce import archiNym, INT
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

# automagical virtual dtype hacks for planar data follow :)
class NpcLocData (memmap, md5Array):
    def _get_x (self):
        return self[...,0]
    def _set_x (self, v):
        self[...,0] = v
    def _get_y (self):
        return self[...,1]
    def _set_y (self, v):
        self[...,1] = v
    def _get_id (self):
        return self[...,2]
    def _set_id (self, v):
        self[...,2] = v

    def _get_dir (self):
        return self[...,3]
    def _set_dir (self, v):
        self[...,3] = v
    def _get_frame (self):
        return self[...,4]
    def _set_frame (self, v):
        self[...,4] = v

    x = property (_get_x,_set_x)
    y = property (_get_y,_set_y)
    id = property (_get_id,_set_id)
    dir = property (_get_dir,_set_dir)
    frame = property (_get_frame,_set_frame)

class DoorLinks (memmap, md5Array):
    def _get_src (self):
        return self[...,0]
    def _set_src (self, v):
        self[...,0] = v
    def _get_dest (self):
        return self[...,1]
    def _set_dest (self, v):
        self[...,1] = v
    def _get_destmap (self):
        return self[...,2]
    def _set_destmap (self, v):
        self[...,2] = v
    def _get_tag1 (self):
        return self[...,3]
    def _set_tag1 (self, v):
        self[...,3] = v
    def _get_tag2 (self):
        return self[...,4]
    def _set_tag2 (self, v):
        self[...,4] = v

    src = property (_get_src,_set_src)
    dest = property (_get_dest,_set_dest)
    destmap = property (_get_destmap,_set_destmap)
    tag1 = property (_get_tag1,_set_tag1)
    tag2 = property (_get_tag2,_set_tag2)

class DoorDefs (memmap, md5Array):
    def _get_x (self):
        return self[...,0]
    def _set_x (self, v):
        self[...,0] = v
    def _get_y (self):
        return self[...,1]
    def _set_y (self, v):
        self[...,1] = v
    def _get_bitsets (self):
        return self[...,2].astype('H')
    def _set_bitsets (self, v):
        self[...,2] = np.asarray(v).astype('H')

    x = property (_get_x,_set_x)
    y = property (_get_y,_set_y)
    bitsets = property (_get_bitsets,_set_bitsets)

### end planar hacks

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
    #XXX RPGDir-isms (raw filenames.)
    def __init__ (self, rpg, n):
        self.rpg = rpg # rpg always comes from MapManager, which means it is already a proxy
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
        result = unpack ('2H',f.read(4))
        if (os.path.getsize (filename) - 11) % (result[0] * result[1]) > 0:
            raise IOError (('map %d file size is not a multiple of W*H+11 bytes' % self.n)+\
                            ' (expected %d*N+11, got %d)' % (result[0]*result[1],
                                                          os.path.getsize (filename) ))
        return result
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
        return self.rpg.data (fname, offset = 11, dtype = 'B', shape = shape)
    def _get_zonemap (self):
        raise NotImplementedError ('zonemaps')
    def _get_doors (self):
        return self.rpg.data ('dox',
                              offset = 600*self.n,
                              type = DoorDefs,
                              shape = (100,3),
                              dtype = INT,
                              order = 'F',)
    def _get_doorlinks (self):
        return self.rpg.data (self.filename % 'd',
                              offset = 7,
                              dtype = INT,
                              shape = (200, 5),
                              type = DoorLinks,
                              order = 'F')
    def _get_npcdefs (self):
        return self.rpg.data (self.filename % 'n',
                              offset = 7,
                              dtype = dt['n'],
                              shape = (100,))
    def _get_npclocs (self):
        return self.rpg.data (self.filename % 'l',
                         offset = 7,
                         dtype = INT,
                         shape = (300,5),
                         order = 'F').view (type = NpcLocData)
    def _get_filename (self):
        return map_filename (self.rpg.path,
                             self.rpg.archinym.prefix,
                             '%s', self.n)

    def __str__ (self):
        fname = self.filename % 't'
        w,h = self._read_header (fname)
        layers = (os.path.getsize (fname) - 11) // (w*h)
        return '<OHRRPGCE Map, %d layers, %03dx%03d>' % (layers, w, h)

    filename = property (_get_filename)
    doors = property (_get_doors)
    doorlinks = property (_get_doorlinks)
    tile = property (_get_tilemap)
    foe = property (_get_foemap)
    wall = property (_get_wallmap)
    zone = property (_get_zonemap)
    npcdefs = property (_get_npcdefs)
    npclocs = property (_get_npclocs)

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
    def _check_id (self, id):
        if type(id) != int:
            raise ValueError ('%r is not a valid map id'
                              ' (not an integer)' % id)
        if id not in self:
            raise ValueError ('%r is not a valid map id'
                              ' (references a map which doesn\'t exist)' % id)
    def __getitem__ (self, k):
        self._check_id (k)
        if k not in self.refs:
            tmp = Map (self.rpg,k)
            self.refs[k] = tmp
        else:
            tmp = self.refs[k]
        return tmp

    def __delitem__ (self, k):
        self._check_id (k)
        raise NotImplementedError('delete map')

class RPGHandler (object):
    _lumpmetadata = {
       'gen' : (7,0), # offset, flags
    }
    def prepare (self):
        self.general = self.data ('gen')
        self.passcode = Passcode (self.general)

class RPGFile (RPGHandler):
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
        self.maps = MapManager (self,)

    def data (self, lump, n = None, dtype = None, offset = None, type = None, **kwargs):
        """Create a memmap pointing at a given kind of lump"""
        boffset, flags = self._lumpmetadata.get(lump, (0, 0))
        if type == None:
            type = OhrData
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
            self.mmaps[filename] = type (filename, mode = self.mode, dtype = dtype, offset = offset, **kwargs)
            return self.mmaps[filename]
        else:
            self.mmaps[filename] = type (filename, mode = self.mode, dtype = dtype, offset = offset, **kwargs)
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
