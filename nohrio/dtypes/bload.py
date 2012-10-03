import numpy as np
import struct
from nohrio.iohelpers import Filelike

BLOAD_SIZE = 7

_FORMAT = '<BHHH'
_MAGIC = 0xfd
_SEGMENT = 0x9999
_OFFSET = 0

def bsave (data, outfile, newformat = False):
    """Save data with BLOAD/BSAVE header to file or filehandle

    :Parameters:
        data : bytes or array
            If an array, the bytes in ``array.data`` are saved
        outfile : filename or filelike object
            Destination
        newformat : boolean, optional
            Save in new format
            (where essentially the header is a meaningless and arbitrary 7 bytes.)
    """
    size = -1
    if type (data) == bytes:
        size = len(data)
    else:
        size = data.nbytes
        # get the array's buffer
        data = data.data
    if (not newformat) and size > 0xffff:
        raise ValueError('Cannot represent %d bytes of data in BSAVE classical format (65535 byte maximum)' % size)
    with Filelike(outfile, 'rb') as f:
        if newformat:
            f.write(b'\x00\x00\x00\x00\x00\x00\x00')
        else:
            f.write(struct.pack(_FORMAT, _MAGIC, _SEGMENT, _OFFSET, size))
        f.write(data)

def bload (infile, newformat_ok = False):
    """Load BSAVE-encapsulated data from file or filehandle.

    :Parameters:
        infile : filename or filelike object
            Input file
        newformat_ok : boolean, optional
            Assume that the input may be new format.
            Disables validating the header, and reads all available content.

    :Returns:
        data : bytes
            the resulting data.
    """
    data = None
    with Filelike(infile, 'rb') as f:
        ssize = struct.calcsize(_FORMAT)
        buffer = f.read(ssize)
        magic, segment, offset, size = struct.unpack(_FORMAT, buffer)
        if newformat_ok:
            size = -1
        if magic != _MAGIC and (not newformat_ok):
            raise ValueError ("Magic value mismatched (got %d, expecting %d)" % (magic, _MAGIC))
        data = f.read(size)
        actual_size = len(data)
        if (not newformat_ok) and actual_size < size:
            raise ValueError ("Expecting %d bytes of data, only got %d" % (size, actual_size))
    return data

__all__ = ('bload', 'bsave', 'BLOAD_SIZE')
