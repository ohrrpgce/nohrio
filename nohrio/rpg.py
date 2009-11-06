# .. note::
#
#    For BLOAD lumps, the BLOAD header needs to be updated after expanding the file.
#

import numpy as np
import os

bload_dtype = np.dtype ([('magic', 'B'),
                         ('segment', '<H'), ('offset', '<H'),
                         ('size', '<H')])

def rewrite_bload (filename, memmap):
    """Rewrite the bload header to match the size of the memmap
       (assuming that the memmap covers all records.)
    """
    tmp = np.memmap (filename, mode = 'wb', offset = 0,
                     dtype = bload_dtype, shape = ())
    tmp['magic'] = 0x7d
    tmp['segment'] = 0x9999
    tmp['offset'] = 0
    tmp['size'] = memmap.itemsize * len(memmap)
    tmp.flush()
    tmp.close()

single = ('FONT', 'GENERAL', 'OLDMASTERPALETTE')
planar = ('DOORLINK', 'DOOR', 'NPCDEF', 'NPCLOC')
bload = ('OLDMASTERPALETTE',)
spliced = ('ATTACKS',)
cache = ('DEFPASS',)
offsets = {'PALETTE' : 16}

shape_instead_of_dtype = {'PALETTE': ((16,), 'B')}

SINGLE = 0x1
PLANAR = 0x2
BLOAD  = 0x4
SPLICED= 0x8
CACHE  = 0x16

from nohrio.ohrrpgce import dtypes, deprecated_dtypes
import struct

# .. todo::
#
#     Now mangle the above into a single table.
#
# and delete the source objects

# key:
#
# '>' = temporary, probably spliced
# '~' = placeholder for 'lump prefix'
# '\\' = special code (currently only 'map' followed by a character).
#        used for disjunct filename schemes (as in when there are >100 maps)


filenames = {

# may change in future, james has a plan to either migrate it to a spliced format
# or a new fileformat altogether (RELOAD).

 'ATTACKS' : '>attack.full',
 'ATTACKGFX' : '~.pt6',
 'BROWSEINFO' : 'browse.txt',
 'DOORLINK' : '\\mapd',
 'ENEMY' : '~.dt1',
 'LARGEENEMYGFX' : '~.pt3',
 'MEDENEMYGFX' : '~.pt2',
 'SMALLENEMYGFX' : '~.pt1',
 'FONT' : '~.fnt',
 'GENERAL' : '~.gen',
 'HERO' : '~.dt0',
 'HEROGFX' : '~.pt0',
 'OLDMASTERPALETTE' : '~.mas',
 'MASTERPALETTE' : 'palettes.bin',
 'NPCDEF' : '\\mapn',
 'PALETTE' : '~.pal',
 'PORTRAITGFX' : '~.pt8',
 'TEXTBOXGFX' : '~.pt7',
 'VEHICLE' : '~.veh',
 'WALKGFX' : '~.pt4',
 'WEAPONGFX' : '~.pt5',
 }

def getdtype (filename):
    if filename.startswith ('~'):
        filename = filename[2:]
        return dtypes.get (filename, deprecated_dtypes.get (filename, None))
    elif filename.startswith ('\\'):
        return dtypes[filename[4:]]
    if filename.startswith('>'):
        filename = filename[1:]
    return dtypes[filename]

info = {}

for name, filename in filenames.items():
    flags = 0
    offset = offsets.get (name, 0)
    shape_dtype_sub = None
    for which, flagval in zip ((single, planar, bload, spliced), (SINGLE, PLANAR, BLOAD, SPLICED)):
        if name in which:
            flags |= flagval
            if flagval == BLOAD:
                offset += 7
    # XXX shape_instead_of_dtype support?
    info[name] = (filename, getdtype(filename), flags, offset)

del single
del planar
del bload
del offsets
del filenames

import re
import numpy as np

# lumpid is like this:
# LUMPIDENTIFIER[SUBSCRIPT]
# where SUBSCRIPT may be one or more slices
# (currently limited to one.)
# [SUBSCRIPT] is optional. omitting it is equivalent to specifying
# all records (as in '[:]')
# slices may not specify a step size -- this is locked at 1
lumpid_rex = re.compile ('((?P<mapid>[0-9]+):)?(?P<lumpid>[A-Za-z0-9]+)'
                         '(\\[(?P<slice>[0-9:]+)\\])?')


def unpack_lumpid (lumpid):
    m = lumpid_rex.match (lumpid)
    dict = m.groupdict()
    for key in dict.keys():
        if dict[key] == None:
            del dict[key]
    dict['lumpid'] = dict['lumpid'].upper()
    return dict

def read_lumpheader (file):
    characters = ['']
    while len(characters) < 14 and characters[-1] != '\x00':
        characters.append (file.read (1))
        if characters[-1] == '':
            if len (characters) != 2:
                raise IOError ('Broken lump header near end of file')
            return None, None, None
    characters = characters[:-1]
    filename = "".join (characters)
    size = file.read(4)
    size = struct.unpack('<I', '%s%s%s%s' % (size[2], size[3],
                                             size[0], size[1]))[0]
    return filename, file.tell(), size


def guess_lump_prefix (lumplist):
    """Given a list of lump names, without path, guess the lump-prefix."""
    leftpart = [v[:v.find('.')] for v in lumplist]
    lump_prefix = None
    unique = set (leftpart)
    for v in unique:
        # in the test data, 43 of the prefix are found
        # in OHRRPGCE.NEW,  38 of the prefix are found out
        # of total 57 lumps
        if leftpart.count(v) > 16:
            lump_prefix = v
            break
    return lump_prefix

class RPG (object):
    def load (self, lumpid, write = False, dtype = None):
        pass
        # return a memmap or array
    def save (self, arr, lumpid):
        # write, creating file if necessary
        pass

    def grow (self, lumpid, newsize, template = None):
        pass

    def upgrade (self, lumpid):
        pass

    def maxrecord (self, lumpid):
        pass

    def recordlength (self, lumpid):
        pass

class RPGFile (RPG):
    """Handler for 'inline' I/O of RPG lumps

    All memmaps returned are explicitly shaped, which means
    (UNTESTED) it's not possible to expand a lump or write beyond its
    end.
    """
    def __init__ (self, filename):
        # build a table of available lumps
        f = open (filename, 'rb')
        self.lump_map = {}
        filename = 'nothing'
        while filename:
            filename, offset, size = read_lumpheader (f)
            if filename:
                self.lump_map[filename] = (offset, size)
                f.seek (offset + size)
        self.lump_prefix = guess_lump_prefix (self.lump_map.keys())
        f.close()

    def load (self, lumpid, write = False, dtype = None):
        lumpdict = unpack_lumpid (lumpid)
        if 'mapid' in lumpdict or 'slice' in lumpdict:
            raise NotImplemented()
        try:
            info = info[lumpid]
        except KeyError:
            if not dtype:
                raise ValueError ('dtype must be specified when loading file directly')
            info = (lumpid, dtype,) + dtype_to_lumpid (dtype)[2:]
        # TODO: handle dtype here
        dtype = info[1]
        flags = info[2]
        offset = info[3]
        order = 'C'
        # TODO: handle slicing here -- alter offset and shape
        filename = info[0]
        baseoffset, basesize = self.lump_map[filename]
        shape = basesize / dtype.itemsize
        if flags & PLANAR:
            order = 'F'
        if flags & SINGLE:
            shape = ()
        mode = "r"
        if write:
            mode = "r+"
        # the following is WRONG.
        # it should ignore filename
        result = np.memmap (filename, dtype = dtype, mode = mode, shape = shape, order = order, offset = baseoffset + offset)
        return result

    def save (self, arr, lumpid):
        lumpdict = unpack_lumpid (lumpid)
        slice = lumpdict['slice']
        id = lumpdict['lumpid']
        if slice > self.maxrecord (lumpid):
            raise NotImplementedError() # TODO: expand the lump as a temporary file.
        if arr.dtype.itemsize != self.recordlength(id):
            raise UpgradeRequired (id, self.recordlength(id))
        if len(arr) != len (slice):
            raise ValueError ("Won't write array"
                  " of inappropriate size %d to %s" % (len(arr), len(slice)))
        pass # XXX actually write something

    def extract (self, destination, lumpname = '*'):
        pass


class RPGDir (RPG):
    def __init__ (self, directory):
        import glob
        self.directory = os.path.abspath (directory)
        self.lumps = glob.glob (os.path.join (directory, '*'))
        self.lumps = [os.path.basename (v) for v in self.lumps]
        # read GEN and notice what our lump prefix is.
        # for now, hackhackhack:
        self.lump_prefix = guess_lump_prefix (self.lumps)

    def load (self, lumpid, write = False, dtype = None):
        lumpdict = unpack_lumpid (lumpid)
        if 'mapid' in lumpdict or 'slice' in lumpdict:
            raise NotImplemented()
        try:
            inforecord = info[lumpdict['lumpid']]
        except KeyError:
            if not dtype:
                raise ValueError ('dtype must be specified when loading file directly')
            inforecord = (lumpid, dtype,) + dtype_to_lumpid (dtype)[2:]
        dtype = inforecord[1]
        flags = inforecord[2]
        offset = inforecord[3]
        order = 'C'
        shape = None
        if flags & PLANAR:
            order = 'F'
        if flags & SINGLE:
            shape = ()
        # TODO: handle slicing here -- alter offset and shape
        filename = inforecord[0]
        if '~' in filename:
            filename = filename.replace ('~', self.lump_prefix)
        if filename not in self.lumps:
            raise IOError ('Lump %r not found in RPGDir!' % filename)
        filename = os.path.join (self.directory, filename)
        mode = "r"
        if write:
            mode = "r+"
        result = np.memmap (filename, dtype = dtype, mode = mode, shape = shape, order = order, offset = offset)
        return result


    pass
