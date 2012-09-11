import functools 
import os
from bits.dtype import OFFSET

CREATOR_NAME = 'nohrio v3'

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
        if self.have_own_handle:
            return self.infile.__exit__(type, value, traceback)
        return True
        

def cp (srcrpg, destrpg, lumpnames):
    """Copy lumps from srcrpg to destrpg.
    srcrpg may be lumped (either a filehandle or a filename) or an rpgdir
    destrpg must be an rpgdir.
    
    Notes
    -------
    
    Enforces case uniformity (lowercase filenames)
    """
    srcishandle = type(srcrpg) != str
    srcrpgname = srcrpg if not srcishandle else srcrpg.name
    srcprefix = os.path.splitext (os.path.basename(srcrpgname))[0] + '.'
    
    destprefix = os.path.splitext (os.path.basename(destrpg))[0] + '.'
    if not srcishandle and os.path.isdir (srcrpg):
        if type(lumpnames) == str and '*' in lumpnames:
            import glob
            lumpnames = [os.path.basename(v) for v in glob.glob(os.path.join(srcrpg, lumpnames))]
        import shutil
        for lumpname in lumpnames:
            srcfilename = os.path.join(srcrpg, lumpname)
            if lumpname.startswith(srcprefix):
                lumpname = lumpname.replace(srcprefix, destprefix)
            destfilename = os.path.join(destrpg, lumpname.lower())
            if not os.path.exists (destfilename):
                shutil.copy(srcfilename, destfilename)
            else:
                raise OSError('Lump already exists in %s' % destrpg)
    else:
        from nohrio.lump import read_lumpheader
        lumpname, offset, length = ('dummy', 1, 1)
        with FilenameOrHandleOpen(srcrpg, 'rb') as f:
            while lumpname != None:
                lumpname, offset, length = read_lumpheader(f)
                if lumpname != None:
                    print ('reading %s (%d bytes)' % (lumpname, length))
                    lumpname = lumpname.lower()
                    destlumpname = (lumpname if not lumpname.startswith(srcprefix) 
                                    else lumpname.replace(srcprefix, destprefix))
                    destlumpname = os.path.join(destrpg, destlumpname) 
                    outf = open(destlumpname, 'wb')
                    while length > 0:
                        thisamount = min (length, 1024*1024)
                        outf.write(f.read(thisamount))
                        length -= thisamount
                    outf.close()
                        
                
        #raise TypeError('lumped rpg not yet supported as source')

def _memmap_bload (filename, dtype, mode = 'r', paddingok = False):
    import numpy as np
    expectedsize = 7 + dtype.itemsize
    # older versions of nose explode at this:
    actualsize = os.path.getsize(filename)
    size_matches = actualsize == expectedsize
    if not size_matches and not (paddingok and actualsize > expectedsize):
        raise OSError('%s : expected size %d, actual %d' % (filename, 
                                                            expectedsize,
                                                            actualsize))
    print ("DTYPE ITEMSIZE: %d" % expectedsize)
    return np.memmap(filename, dtype, mode = mode, offset=7, shape = ())

def create(name, template = 'ohrrpgce.new', creator=None, **gen_updates):
    """Create an RPGDir of the specified name from a template,
    updating 0 or more of the fields in GEN."""
    print ('Creating from %s' % template)
    import nohrio.dtypes.general
    creator = creator or CREATOR_NAME
    os.mkdir(name)
    cp (template, name, '*')
    if '%s' in creator:
        creator = creator % CREATOR_NAME
    prefix = os.path.basename(name)
    archinym = '\n'.join((prefix, creator)) + '\n'
    with open (os.path.join(name, 'archinym.lmp'), 'w') as f:
        f.write (archinym)
    if len(gen_updates):
        print (gen_updates)
        fdtype = nohrio.dtypes.general.DTYPE.freeze()
        array = _memmap_bload (os.path.join(name, prefix + '.gen'), fdtype, mode = 'r+')
        for k,v in gen_updates.items():
            array[k] = v
        array.flush()
        
    # XXX update archinym.

rpg_creator = lambda **kwargs: functools.partial(create, **kwargs)