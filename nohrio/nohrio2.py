#coding=utf8
import functools
import os
from bits import copyattr
from bits.subfile import SubFile
from nohrio.dtypes.archinym import Archinym
from nohrio.dtypes.general import GeneralData, BrowseInfo, CURRENT_FORMAT
from nohrio.iohelpers import Filelike, FilelikeLump
from collections import namedtuple
import numpy as np

CREATOR_NAME = 'nohrio v3'
STANDARD_SIZES = {
                  '*.gen' : 1007,
                  }

# ubiquitous dtype used throughout OHRRPGCE
INT = np.dtype ('<h')

def cp (srcrpg, destrpg, lumpnames):
    """Copy lumps from srcrpg to destrpg.
    srcrpg may be lumped (either a filehandle or a filename) or an rpgdir
    destrpg must be an rpgdir.

    :Notes:
        Enforces case uniformity by lowercasing all filenames.
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
        with Filelike(srcrpg, 'rb') as f:
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

def ls (rpg):
    """Return a list of (filename, offset, size) tuples, one for each file in the rpg."""
    # rpgdir? easy!
    if os.path.isdir(rpg):
        import glob
        return [(fname, os.path.getsize(fname)) for fname in glob.glob(os.path.join(rpg,'*'))]
    contents = []
    from nohrio.lump import read_lumpheader
    lumpname = 'dummy'
    with Filelike(rpg, 'rb') as f:
        while lumpname != None:
            lumpname, offset, length = read_lumpheader(f)
            if lumpname != None:
                lumpname = lumpname.lower()
                contents.append((lumpname, offset, length))
                f.seek(length,1)
    return contents


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

def sanity_check(name, prefix):
    """Return True if the specified rpgdir looks sane,
    otherwise a list of missing files or characteristics."""
    errors = []
    def check (lumpname, expected_size = None):
        path = os.path.join(name, lumpname)
        ok = os.path.exists(path)
        if not ok:
            errors.append(lumpname)
        if expected_size:
            actual_size = os.path.getsize (path)
            ok = actual_size == expected_size
            if not ok:
                errors.append((lumpname,'size', actual_size))
    # TODO: also check fixbits and add any 'missing' fixes to the missing list
    for lumpname, size in STANDARD_SIZES.items():
        print ('LS', lumpname, size)
        lumpname = lumpname.replace('*', prefix)
        check (lumpname, size)
    # TODO: report when gen.rpgversion is higher than we know of.
    if not errors:
        return True
    return missing

def openrpgdirlump(self, lump, mode):
    return open(os.path.join(self.source, lump), mode)

def openrpglump(self, lump, mode):
    tmp = open(self.source, mode)
    print ('opened %r, mode %r' % (self.source, mode))
    dest = self.index[lump].offset
    print ('seeking to %r' % dest)
    tmp.seek(dest)
    tmp = SubFile(tmp, self.index[lump].size)
    print (tmp)
    return tmp


SubLumpInfo=namedtuple('SubLumpInfo', 'offset size')

class RPG(object):
    """R/W, Object oriented access to RPG contents.

    :Parameters:
        source: path to file or directory
        mode: str
            'r' or 'r+'
        function: function accepting (lump, mode) params, returning context manager.
            Used to get a filehandle when reading/writing lumps.
            If you don't specify this, it's automatically chosen
            according to whether source points at rpg or rpgdir.
    """

    def __init__(self, source, mode=None, function=None):
        if mode not in ('r','r+'):
            raise ValueError('Mode flag %r not understood (should be one of (r r+))' % mode)
        if not os.path.exists (source):
            raise OSError ('File/rpgdir %r doesn\'t exist!' % source)

        isrpgdir = os.path.isdir(source)
        self.source = source
        function = function or (openrpgdirlump if isrpgdir else openrpglump)
        self._openlump = function
        print ('openlump set to %r' % self._openlump)
        self.isrpgdir = isrpgdir
        self.mode = mode + 'b'
        if not isrpgdir:
            self.index = {}
            for name, offset, size in ls(source):
                self.index[name] = SubLumpInfo(offset, size)
            print(self.index)
#            raise NotImplementedError()

        with self.openlump('archinym.lmp') as f:
            print ('fh', f)
            self.arch = Archinym (source=f)

        if isrpgdir:
            sanity_check (source, self.arch.prefix)

        with self.openlump('gen') as f:
            self.gen = GeneralData (f)
            fmtversion = self.gen.formatversion
            if fmtversion != CURRENT_FORMAT:
                if fmtversion > CURRENT_FORMAT:
                    print('RPGFile version %d is newer than'
                          ' the format understood by nohrio (%d)' % (fmtversion, CURRENT_FORMAT))
                else:
                    print('RPGFile version %d is older than'
                          ' the format understood by nohrio (%d)' % (fmtversion, CURRENT_FORMAT))


        with self.openlump('browse.txt') as f:
            browse = BrowseInfo(f)
            copyattr(browse, self,'about','longname')

    def lumpname(self, lump):
        return self.arch.lumpname(lump)

    def openlump(self, lump, mode = None):
        """Return a file handle pointing to a given lump.

        """
        mode = mode or self.mode
        # naturally self.arch is not available until archinym.lmp is loaded.
        if lump != 'archinym.lmp':
            lump = self.lumpname(lump)
        return self._openlump(self, lump, mode)
        #if self.isrpgdir:
            #return FileLike(lump, mode=mode)
        #self.source.seek(self.index[lump])
        #return FileLike(index[lump]

if __name__ == "__main__":
    r = RPG('../tests/ohrrpgce.new', 'r')
    print (r.arch)
    print (r.about,'|', r.longname)






def open_rpg(name, mode):
    if mode not in ('r','r+'):
        raise ValueError('Mode flag %r not understood (should be one of (r w r+))' % mode)
    # for now we only handle 'r'
    if mode != 'r':
        raise NotImplementedError()
    if not os.path.exists (name):
        raise OSError ('File/rpgdir %r doesn\'t exist!' % name)
    is_rpgdir = os.path.isdir(name)
    if not is_rpgdir:
        raise NotImplementedError()
    arch = Archinym (name)
    sanity_check (name, arch.prefix)


# do this instead of subclassing unnecessarily:
#FormatNotSupported = lambda v: NotImplementedError('Format not supported: %r' % v)


#raise FormatNotSupported('foo')
