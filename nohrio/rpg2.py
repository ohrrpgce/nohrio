from numpy import memmap
import numpy as np
from nohrio.lump import read_lumpheader, lumpname_ok, Passcode
import os
from nohrio.dtypes import GENERAL, dt
from nohrio.ohrrpgce import archiNym, INT
from weakref import proxy, WeakValueDictionary
from struct import unpack

from nohrio.wrappers import *

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
