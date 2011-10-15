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
bload = ('OLDMASTERPALETTE', 'GENERAL')
spliced = ('ATTACKS',)
cache = ('DEFPASS',)
offsets = {'PALETTE' : 16}
binsized = {'MENU' : 'menu'}

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
#

 'ATTACKS' : '>attack.full',
 'ATTACKGFX' : '~.pt6',
 'BACKGROUND' : '~.mxs',
 'BINARYSIZE' : 'binsize.bin',
 'BROWSEINFO' : 'browse.txt',
 'DEFAULTPASS' : 'defpass.bin',
 'DEFAULTPALETTE' : 'defpal%d.bin',
 'DOORLINK' : '\\mapd',
 'DOOR' : '~.dox',
 'ENEMY' : '~.dt1',
 'LARGEENEMYGFX' : '~.pt3',
 'MEDENEMYGFX' : '~.pt2',
 'SMALLENEMYGFX' : '~.pt1',
 'FONT' : '~.fnt',
 'FORMATION' : '~.for',
 'FORMATIONSET' : '~.efs',
 'GENERAL' : '~.gen',
 'HERO' : '~.dt0',
 'HEROGFX' : '~.pt0',
 'ITEM' : '~.itm',
 'MAPINFO' : '~.map',
 'MAPNAME' : '~.mn',
 'OLDMASTERPALETTE' : '~.mas',
 'MASTERPALETTE' : 'palettes.bin',
 'MENU' : 'menus.bin',
 'MENUITEM' : 'menuitem.bin',
 'NPCDEFINITION' : '\\mapn',
 'NPCLOCATION' : '\\mapl',
 'PALETTE' : '~.pal',
 'PORTRAITGFX' : '~.pt8',
 'SCRIPTLIST' : 'plotscr.lst',
 'SFXINFO' : 'sfxdata.bin',
 'SHOP' : '~.sho',
 'SONGINFO' : 'songdata.bin',
 'TAGNAME' : '~.mn',
 'TEXTBOX' : '~.say',
 'TEXTBOXGFX' : '~.pt7',
 'TILESET' : '~.til',
 'TILEANIMATION' : '~.tap',
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
    # XXX incorporate binsized data support
    info[name] = (filename, getdtype(filename), flags, offset)

del single
del planar
del bload
del offsets
del filenames

import re
import numpy as np

from nohrio.lump import *

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
        self.lump_map = read_lumplist(f)[1]
        if not lumpnames_dont_collide (lump_map.keys()):
            raise IOError ('Conflicting lump names (duplicated, or identical except for case)')

        self.lump_prefix = guess_lump_prefix (self.lump_map.keys())
        f.close()

    def load (self, lumpid, write = False, dtype = None):
        lumpdict = unpack_lumpid (lumpid)
        if 'mapid' in lumpdict or 'slice' in lumpdict:
            raise NotImplementedError()
        try:
            inforecord = info[lumpid]
        except KeyError:
            if not dtype:
                raise ValueError ('dtype must be specified when loading file directly')
            inforecord = (lumpid, dtype,) + dtype_to_lumpid (dtype)[2:]
        # TODO: handle dtype here
        dtype = inforecord[1]
        flags = inforecord[2]
        offset = inforecord[3]
        order = 'C'
        # TODO: handle slicing here -- alter offset and shape
        filename = inforecord[0]
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
        for filename in self.lumps:
            if not self.lumpname_ok (filename):
                raise IOError ('corrupted or non canonical lump name %r' % filename)

        if not lumpnames_dont_collide (lumps):
            raise IOError ('Conflicting lump names (duplicated, or identical except for case)')

        # read GEN and notice what our lump prefix is.
        # for now, hackhackhack:
        self.lump_prefix = guess_lump_prefix (self.lumps)

    def load (self, lumpid, write = False, dtype = None):
        lumpdict = unpack_lumpid (lumpid)
        if 'mapid' in lumpdict or 'slice' in lumpdict:
            raise NotImplementedError()
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
        result = np.memmap (filename, dtype = dtype, mode = mode,
                            shape = shape, order = order,
                            offset = offset)
        return result

