import numpy as np
from collections import namedtuple
from bits import Enum, AttrStore
from bits.dtype import DType
from nohrio.iohelpers import IOHandler, Filelike
from nohrio.dtypes.common import (PalettedPic, Coords, scalararray,
                                  readstr, writestr, copyfrom)
from nohrio.dtypes.bload import BLOAD_SIZE


class NPCZoning(AttrStore):
    def __init__(self, stayinside = -1, stayoutside = -1):
        self.stayoutside = stayoutside
        self.stayinside = stayinside

class NPCDef(AttrStore):
    dtype = DType('h:picture: h:palette: h:movetype: h:speed: h:showtext: '
                'h:activate_action: h:giveitem: h:pushability: h:activation: '
                'h:appear_if_tag1: h:appear_if_tag2 h:usability: h:trigger:',
                'h:script_arg: h:vehicle:'
                'h:defzonerestriction: h:defavoidancezone')
    def __init__(self, appearance, appear_tags, movetype, speed,
                 trigger = ScriptTrigger(), zoning = NPCZoning(),
                 source = None):

    def save(self, fh):

class NPCDefs(IOHandler, AttrStore):
    def __init__(self, source, binsize=15, rpgversion=MAX_RPGVERSION):
        dtype = binsizize (NPCDef.dtype, binsize)
        with Filelike(source, 'rb') as fh:
            _ = fh.read(BLOAD_SIZE)
            # read data, pad/cut dtype according to binsize, set self._data
            nrecords = -1  # zenzizenic determines nrecords from amount of data in the lump.
            wastedrecords = 0
            if rpgversion <= RPGVER_WEREWAFFLE:
                nrecords = 36
                wastedrecords = 64
            elif rpgversion >= RPGVER_XOCOLATL:
                nrecords = 100
            if nrecords != -1:
                rawdata = fh.read(nrecords * dtype.itemsize)
            else:
                rawdata = fh.read()
            if wastedrecords:
                _ = fh.read(wastedrecords * dtype.itemsize)
            ohrdata = binsized_array_from_string (rawdata,
                                                 src=dtype, dest=NPCDef.dtype)
            reformatted_array = np.zeros_like(ohrdata)
            _data = reformatted_array
    def save(self, fh, binsize)
        # unpad data per binsize,
        # dump to file
        pass

    def __getitem(self, k):
        if k < 0 or k >= len(self._data):
            raise ValueError('Invalid NPCDef index %d ' % k)
        return NPCDef(*self._data[k])

if __name__ == "__main__":
    n = NPCDefs('../../ohrrpgce/vikings/vikings.rpgdir/viking.n00')
    print(n)
