from nohrio.iohelpers import FilenameOrHandleOpen
import numpy as np
import struct

_FORMAT = '>BHHH'
_MAGIC = 0x7d
_SEGMENT = 0x9999
_OFFSET = 0

def bsave (data, f):
    """Save data with BLOAD/BSAVE header to file or filehandle"""
    size = -1
    if type (data) == bytes:
        size = len(data)
    else:
        size = data.nbytes
        # get the array's buffer
        data = data.data
    if size > 0xffff:
        raise ValueError('Cannot represent %d bytes of data in BSAVE format (65535 byte maximum)' % size)
    with FilenameOrHandleOpen(f):
        struct.pack(_FORMAT, _MAGIC, _SEGMENT, _OFFSET, size)
        f.write(data)

def bload (infile):
    """Load BSAVE-encapsulated data from file or filehandle.
    
    Returns
    --------
    data : bytes
        the resulting data.
    
    """
    data = None
    #pudb.set_trace()
    with FilenameOrHandleOpen(infile) as f:
        ssize = struct.calcsize(_FORMAT)
        buffer = f.read(ssize)
        print (repr(buffer))
        magic, segment, offset, size = struct.unpack(_FORMAT, buffer)
        if magic != _MAGIC:
            raise ValueError ("Magic value mismatched (got %d, expecting %d)" % (magic, _MAGIC))
        data = f.read(size)
        actual_size = len(data)
        if actual_size < size:
            raise ValueError ("Expecting %d bytes of data, only got %d" % (size, actual_size))
    return data

__all__ = ('bload', 'bsave')