import os
import struct

class FilenameOrHandleOpen (object):
    """Wrapper context-manager which acts like open() when input is a filename, and leaves the handle unchanged otherwise"""
    def __init__(self, infile, *args, **kwargs):
        self.have_own_handle = (type(infile) == str)
        self.infile = infile
        self.args = args
        self.kwargs = kwargs

    def __enter__ (self):
        if self.have_own_handle:
            self.infile = open(self.infile, *self.args, **self.kwargs)
            return self.infile.__enter__()
        return self.infile

    def __exit__ (self, type, value, traceback):
        #print ('exiting', type, value, traceback)
        if self.have_own_handle:
            return self.infile.__exit__(type, value, traceback)
        return (type == StopIteration)

def LumpOrHandleOpen (infile, lumpname, *args, **kwargs):
    if type(infile) == str:
        if not os.path.isdir(infile):
            raise ValueError('Attempting to open lump file inside %r, but it isn\'t a directory!' % infile)
        infile = os.path.join(infile, lumpname.lower())
    return FilenameOrHandleOpen (infile, *args, **kwargs)

class IOHandler(object):
    """Save/Load records

    """
    def save(self, file, *args, **kwargs):
        """Save to a specified file or filehandle, or the source file.

        Parameters
        --------
        file : open file handle or filename
        """
        with FilenameOrHandleOpen(file, 'wb') as fh:
            self._save(fh, *args, **kwargs)

    # NOTE: No 'self'!
    # this method operates as both a standard class method -- save(self, file, *args, *kwargs)
    # and as a static method -- save(file, *args, *kwargs
    def load(cls_or_self, file, *args, **kwargs):
        """Load data from file or filehandle, or the source file

        Parameters
        --------
        cls_or_self : IOHandler instance or subclass
        file : open file handle or filename

        Returns
        --------
        out : self or newly allocated instance
            If this instance cannot accommodate the data, a new instance is created and returned.

        Notes
        ------
        Calls `cls._load(self, opened_filehandle)`.
        self may be a class instead of an instance --
        load_ must cope with this if it needs to support creating new objects,
        rather than merely copying into an existing instance.



        """
        self = cls_or_self
        cls = cls_or_self
        if isinstance(self, IOHandler):
            cls = self.__class__
        ret = None
        with FilenameOrHandleOpen(file, 'rb') as fh:
            ret = cls._load(self, fh, *args, **kwargs)
        return ret

    def _load_struct (self, fh):
        """Unpack data from fh according to self._struct.

        Returns
        --------
        out : tuple of data items
        """
        return self._struct.unpack(fh.read(self._struct.size))

    def _save_struct (self, fh, *args):
        fh.write(self._struct.pack(*args))

def dtype2struct (dtype, can_simplify = False):
    if not dtype.names:
        byteorder = dtype.byteorder
        if byteorder == '|':
            byteorder = '@'
        char = dtype.char
        if char in 'egFDGUSVOMm':
            if (not can_simplify) or char in 'gFDGUVO':
                raise ValueError("%r cannot be converted to a struct code" % dtype)
            char = 'HsQQ'['eSMm'.index(char)]
        return struct.Struct(byteorder + char)
    raise NotImplementedError('Conversion of multi-field dtypes')

#def record_offset (arr,
