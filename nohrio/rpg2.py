"""OO RPGDir/RPGFile access.


"""

from numpy import memmap
import numpy as np
from nohrio.lump import read_lumplist, Passcode, lump
import os
from nohrio.dtypes import GENERAL, dt
from nohrio.ohrrpgce import archiNym, binSize, INT
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
        if result[0] < 16 or result[1] < 10:
            raise ValueError ('Map size %dx%d is too small! (minimum 16x10)' % result)
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
    def _get_name (self):
        tmp = self.rpg.data('mn')[self.n]
        tmp = list (tmp)
        return tmp[1][:tmp[0]]
    def _set_name (self):
        tmp = self.rpg.data('mn')[self.n]
        if len (v) > 79:
            raise ValueError ('map name %s exceeds 79 characters in length' % v)
        tmp['length'] = len (v)
        tmp['value'] = v
    def _get_info (self):
        #XXX use binsize
        return (self.rpg.data ('map')[self.n]).view(OhrDataMemmap)

    def __str__ (self):
        fname = self.filename % 't'
        w,h = self._read_header (fname)
        layers = (os.path.getsize (fname) - 11) // (w*h)
        return '<OHRRPGCE Map %r, %d layers, %03dx%03d>' % (self.name, layers, w, h)

    filename = property (_get_filename)
    name = property (_get_name, _set_name)
    info = property (_get_info)
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
    """Base class for RPG databases.

    Enforces neutral case upon lump names, incidentally.
    """
    _lumpmetadata = {
       'gen' : (7,0), # offset, flags
    }
    def prepare (self):
        self.general = self.data ('gen')
        #self.passcode = Passcode (self.general)
        self.binsize = binSize (self.lump_path('binsize.bin'))
        #XXX fixbits
    def rename (self, newname):
        """Rename the rpg file/dir, adjusting the lumps and ARCHINYM.LMP
        accordingly.
        """
        raise NotImplementedError()
    def _pal16 (self):
        # XXX assuming new non-bload format
        return self.data ('.pal', offset = 16)
    def _pal256 (self):
        # XXX assuming new non-MAS format
        if self.has_lump ('palettes.bin'):
            return self.data (self.lump_path ('palettes.bin'),
                              dtype = [('r', np.uint8),
                                       ('g', np.uint8),
                                       ('b', np.uint8)],
                              offset = 4)

    pal16 = property (_pal16)
    pal256 = property (_pal256)

class RPGFile (RPGHandler):
    """RPGFile reader/writer.
    """
    def __init__ (self, filename, mode = 'r', unlumpto = None):
        needs_close = False
        openmode = mode
        if 'b' not in mode:
            openmode += 'b'
        else:
            raise ValueError ('mode must not contain "b" (see numpy.memmap docs)')
        f = open (filename, openmode)
        # mapping, step 1: Detect all lumps.
        self.path = filename
        if unlumpto:
            self.unlump_dir = unlumpto
            self.rm_unlump_dir = False
        else:
            from tempfile import mkdtemp
            from os.path import basename
            if filename:
                self.unlump_dir = mkdtemp (os.path.basename (filename))
            else:
                self.unlump_dir = mkdtemp ()
            self.rm_unlump_dir = True
        self.manifest, self._lump_map = read_lumplist (f)
        self.mode = mode
        # mapping, step 2: create corresponding objects for the lumps we know
        # Mapping, final step: catalogue all lumps we don't understand.
        # Init, step 1: read GEN
        # Init, step 2: decode password, creating Passcode object.
        #passcode = Passcode (self.general)
        # unlump
        if needs_close:
            f.close()
    def __len__ (self):
        return len (self._lump_map)
    def unlump_all (self, dest = None):
        ordered = self._lump_map.keys()
        ordered.sort (key = lambda v:v[1][0])
        #read them in order.
        #yield after each lump, so that showing a progress bar is easy.
        #
        for lumpname in ordered:
            yield dest or self.unlump_dir
            self.unlump (lumpname, dest)
    def unlump (self, filename, dest = None):
        "Unlump a lump, return its final filename with path."
        filename = filename.lower()
        if filename not in self._lump_map:
            raise ValueError ('asked for %r: not a known lump within this RPGFile' % filename)
        offset, size = self._lump_map[filename]
        if not dest:
            dest = self.unlump_dir
        dest = os.path.join (dest, filename)
        with open (dest, 'wb') as out:
            with open (self.path, 'rb') as f:
                f.seek (offset)
                out.write (f.read (size))
        return dest
    def __del__ (self):
        if self.rm_unlump_dir:
            import glob
            for fn in glob.glob (os.path.join (self.unlump_dir, '*')):
                os.remove (fn)
            try:
                os.rmdir (self.unlump_dir)
            except OSError:
                pass


class RPGDir (RPGHandler):
    def __init__ (self, path, mode):
        import glob
        filenames = glob.glob (os.path.join (path,'*') )
        # classify filenames into old-style: WANDER.XYZ
        # and new style: XYZ.ABC
        if 'b' in mode:
            raise ValueError ('mode must not contain "b" (see numpy.memmap docs)')
        self.archinym = archiNym (os.path.join (path, 'archinym.lmp'))
        if self.archinym.prefix == '':
            self.archinym.prefix = os.path.splitext (os.path.basename (path))[0]
        self.manifest = filenames
        from weakref import WeakValueDictionary
        self.mmaps = {}
        self.mode = mode
        self.path = path
        self.prepare()
        self.maps = MapManager (self,)
    def lump_all (self, dest):
        tmp = list (self.manifest)
        tmp.sort()
        genname = os.path.join (self.path, self.archinym.prefix + '.gen')
        archname = os.path.join (self.path, 'archinym.lmp')
        if genname not in tmp:
            raise IOError ('Missing .GEN lump from %s' % self.path)
        tmp.remove (genname)
        tmp.remove (archname)
        tmp.insert (0, genname) # GEN second-from-front
        tmp.insert (0, archname) # ARCHINYM.LMP at front.
        needs_close = False
        if type (dest) in (str, unicode):
            if os.path.exists (dest):
                raise OSError ('Refusing to lump a RPG over the top of an existing file')
            dest = open (dest, 'wb')
            needs_close = True
        for item in tmp:
            lump (item, dest)
        if needs_close:
            dest.close()
    def lump (self, which, dest):
        lump (which, dest)
    def data (self, lump, n = None, dtype = None, offset = None, type = None, **kwargs):
        """Create a memmap pointing at a given kind of lump"""
        boffset, flags = self._lumpmetadata.get(lump, (0, 0))
        if type == None:
            type = OhrDataMemmap
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
            filename = self.lump_path (os.path.basename (lump))
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
        if lump.startswith('.'):
            lump = lump [1:]
        if not "." in lump:
            filename = os.path.join (self.path, self.archinym.prefix + "." + lump)
        else:
            filename = os.path.join (self.path, lump)
        #if filename in self.manifest:
        return filename
    def lump_size (self, lump):
        if not os.path.isfile (lump):
            return 0
        return os.path.getsize (lump)

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

def create (dest, prefix, template = None,
            version = 'nohrio???', dir = False):
    """Create a new RPG file or dir, possibly from a template.
    ARCHINYM.LMP info will be rewritten.

    Returns the path to the new rpgfile or rpgdir.
    """
    import glob
    if len (prefix) > (50-4):
        raise ValueError ('lump prefix too long')
    if os.path.exists (dest):
        raise OSError ('Refusing to create a RPG over the top of an existing file/dir')
    tmpfile = None
    filename = None
    if not template:
        import _newrpg
        from tempfile import mkstemp
        from cStringIO import StringIO as SIO
        data = _newrpg.gunzip ()
        tmpfile = mkstemp (prefix)[1]
        f = open (tmpfile,'wb')
        f.write (data); f.close()
        filename = tmpfile
    else:
        filename = template
    rpg = RPGFile (filename, 'r')
    tempdir = list (rpg.unlump_all ())[0]
    if tmpfile:
        os.remove (tmpfile)
    lmppath = os.path.join (tempdir,'archinym.lmp')
    from ohrrpgce import archiNym
    # archiNym implicitly writes a new file, when opened on a
    # nonexistent path.  This is weird behaviour and I hope
    # to remedy it.
    a = archiNym (lmppath, 0, prefix, version)
    #now rename all relevant lumps to match.
    for filename in glob.glob (os.path.join (tempdir,'*')):
        if os.path.basename (filename).startswith('ohrrpgce.'):
            parts = os.path.split (filename)
            newfilename = parts[-1].replace('ohrrpgce.', prefix + '.')
            newfilename = os.path.join (parts[0], newfilename)
            os.rename (filename, newfilename)
    # XXX we need to check that all source lumps are arriving safely!
    # since we generate a file 10k smaller currently..
    if not dir:
        rpgdir = RPGDir (tempdir, 'r')
        rpgdir.lump_all (dest)
        return dest
    else:
        #XXX this will fail if the move is over filesystem boundaries IIRC
        os.rename (tempdir, dest)
        return dest

