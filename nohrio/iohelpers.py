import os
import struct

class Filelike (object):
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

def FilelikeLump (infile, lumpname, *args, **kwargs):
    if type(infile) == str:
        if not os.path.isdir(infile):
            raise ValueError('Attempting to open lump file inside %r, but it isn\'t a directory!' % infile)
        infile = os.path.join(infile, lumpname.lower())
    return Filelike (infile, *args, **kwargs)

class IOHandler(object):
    """Save/Load records

    """
    def save(self, file, *args, **kwargs):
        """Save to a specified file or filehandle, or the source file.

        :Parameters:
            file : open file handle or filename
        """
        with Filelike(file, 'wb') as fh:
            self._save(fh, *args, **kwargs)

    def reloadfrom(self, file, *args, **kwargs):
        """Load data from file or filehandle, or the source file,
           into self (in-place)

        :Parameters:
            file : open file handle or filename

        """
        if not hasattr(self, '_reloadfrom'):
            raise NotImplementedError ('%s.reloadfrom()' % self.__class__)
        with Filelike(file, 'rb') as fh:
            return self._reloadfrom(fh, *args, **kwargs)

    def load(file, *args, **kwargs):
        raise TypeError('Class doesn\'t implement load()')

    def _load_struct (self, fh):
        """Unpack data from `fh` according to `self.struct`.

        :Parameters:
            self : IOHandler subclass or instance
            fh : open file handle supporting read()

        :Returns:
            unpacked : tuple of data items

        .. note::

            * self.struct must be a struct.Struct object
              rather than a format-string.

            * self may be a class instead of an instance.

        """
        return self.struct.unpack(fh.read(self.struct.size))

    def _save_struct (self, fh, *args):
        """Pack data into `fh` according to `self.struct`

        """
        fh.write(self.struct.pack(*args))

def dtype2struct (dtype, can_simplify = False):
    """Convert a dtype into a struct format.

    :Parameters:
        dtype : dtype
            A simple scalar or flat structured dtype.
            Nested dtypes will raise an error,
            as struct is incapable of expressing them.
        can_simplify : bool
            True if it's okay to simplify NumPy types that
            have no direct equivalent into formats of a different kind but same
            size.

    .. warning::

        Not all NumPy scalar dtypes can be expressed as struct formats.
        Some (float16, datetime64, timedelta64) can be held as a single value
        of the wrong type (integer);
        This casting will occur if can_simplify == True.

    """
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

def loadstruct (cls,fh):
    """Create a new instance of cls, where cls has a 'struct' field
    ... which matches the order and number of arguments for cls.__init__()"""
    return cls(*IOHandler._load_struct(cls, fh))


#def record_offset (arr,
