single = ('GENERAL',)
planar = ('NPCDEF', 'DOORLINK')
bload = ('OLDMASTERPALETTE',)
spliced = ('ATTACKS',)
offsets = {'PALETTE' : 16}

SINGLE = 0x1
PLANAR = 0x2
BLOAD  = 0x4
SPLICED= 0x8

from nohrio.ohrrpgce import dtypes, deprecated_dtypes

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
 'BROWSEINFO' : 'browse.txt',
 'DOORLINK' : '\\mapd',
 'ENEMY' : '~.dt1',
 'FONT' : '~.fnt',
 'GENERAL' : '~.gen',
 'HERO' : '~.dt0',
 'OLDMASTERPALETTE' : '~.mas',
 'MASTERPALETTE' : 'palettes.bin',
 'NPCDEF' : '\\mapn',
 'PALETTE' : '~.pal',
 'VEHICLE' : '~.veh',
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
    for which, flagval in zip ((single, planar, bload, spliced), (SINGLE, PLANAR, BLOAD, SPLICED)):
        if name in which:
            flags |= flagval
    info[name] = (filename, getdtype(filename), flags, offsets.get(name, 0))

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
                         '(\\[(?P<slice>[0-9:]+)\\])')


def unpack_lumpid (lumpid):
    m = lumpid_rex.match (lumpid)
    return m.groupdict()

class RPG (object):
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
        dtype = info[1]
        flags = info[2]
        offset = info[3]
        order = 'C'
        shape = None
        if flags & PLANAR:
            order = 'F'
        if flags & SINGLE:
            shape = ()
        # TODO: handle slicing here -- alter offset and shape
        filename = info[0]
        mode = "r"
        if write:
            mode = "r+"
        result = np.memmap (filename, dtype = dtype, mode = mode, shape = shape, order = order, offset = offset)
        return result
        # return a memmap or array
    def save (self, arr, lumpid):
        # write, creating file if necessary
        pass

    def grow (self, lumpid, newsize, template = None):
        pass

class RPGFile (RPG):
    """Handler for 'inline' I/O of RPG lumps

    All memmaps returned are explicitly shaped, which means
    (UNTESTED) it's not possible to expand a lump or write beyond its
    end.
    """
    def __init__ (self, filename):
        # build a table of available lumps
        pass

    def load (self, lumpid, write = False):
        pass

    def save (self, arr, lumpid):
        pass

    def extract (self, destination, lumpname = '*'):
        pass


class RPGDir (RPG):
    pass
