import os

class FilenameOrHandleOpen (object):
    """Wrapper context-manager which acts like open() when input is a filename, and leaves the handle unchanged otherwise"""
    def __init__(self, infile, *args, **kwargs):
        self.have_own_handle = (type(infile) == str)
        print ('have own handle? %r' % self.have_own_handle)
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
    def save(self, file):
        "Save to a specified file or filehandle"
        with FilenameOrHandleOpen(file, 'wb') as fh:
            self._save(fh)
        
    def load(self, file):
        """Load data from file or filehandle.
        
        Returns
        --------
        out : self or newly allocated instance
            If this instance cannot accommodate the data, a new instance is created and returned.
        """
        ret = None
        with FilenameOrHandleOpen(file, 'rb') as fh:
            ret = self._load(fh)
        return ret