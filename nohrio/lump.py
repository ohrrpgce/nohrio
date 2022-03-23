import re
import struct

# lumpid is like this:
# LUMPIDENTIFIER[SUBSCRIPT]
# where SUBSCRIPT may be one or more slices
# (currently limited to one.)
# [SUBSCRIPT] is optional. omitting it is equivalent to specifying
# all records (as in '[:]')
# slices may not specify a step size -- this is locked at 1
lumpid_rex = re.compile ('((?P<mapid>[0-9]+):)?(?P<lumpid>[A-Za-z0-9]+)'
                         '(\\[(?P<slice>[0-9:]+)\\])?')

class CorruptionError(IOError):
    pass


def unpack_lumpid (lumpid):
    m = lumpid_rex.match (lumpid)
    dict = m.groupdict()
    for key in list(dict.keys()):
        if dict[key] == None:
            del dict[key]
    dict['lumpid'] = dict['lumpid'].upper()
    return dict

def read_lumpheader (file):
    filename = b''
    while len(filename) < 50:
        ch = file.read(1)
        if not ch:
            if len(filename):
                raise CorruptionError('Broken lump header near end of file')
            return None, None, None
        if ord(ch) == 0:
            break
        filename += ch
    filename = filename.decode('latin-1')
    size = file.read(4)
    size = bytes([size[2], size[3], size[0], size[1]])
    size = struct.unpack('<I', size)[0]
    return filename, file.tell(), size


def write_lumpheader (srcpath, file):
    """

    >>> f = open ('/tmp/testlmp','wb')
    >>> s = 'LUMP DATA!!!!!!!'
    >>> f.write ('LUMP DATA!!!!!!!')
    >>> f.close ()
    >>> from cStringIO import StringIO as SIO
    >>> f = SIO()
    >>> write_lumpheader (f, '/tmp/testlmp')
    >>> f = SIO (f.getvalue())
    >>> name, offset, size = read_lumpheader (f)
    >>> name == 'testlmp'
    True

    >>> size == len(s)
    True
    """
    import os
    base = os.path.basename(srcpath)
    size = os.path.getsize (srcpath)
    if len (base) > 50:
        raise ValueError ('excessively long lump name %r' % base)
    if '\x00' in base:
        raise ValueError ('invalid NULs in lump name %r' % base)
    file.write(base)
    file.write('\x00')
    for v in ((size >> 16) & 0xff, (size >> 24) & 0xff  ,size & 0xff, (size >> 8) & 0xff):
        file.write(chr(v))

def lump (srcpath, file):
    import os
    if not os.path.exists (srcpath):
        raise ValueError ('Can\'t lump from a nonexistent source %r!' % srcpath)
    write_lumpheader (srcpath, file)
    f = open (srcpath, 'rb')
    file.write (f.read())
    f.close()

def guess_lump_prefix (lumplist):
    """Given a list of lump names, without path, guess the lump-prefix."""
    leftpart = [v[:v.find('.')] for v in lumplist]
    unique = set (leftpart)
    for v in unique:
        # in the test data, 43 of the prefix are found
        # in OHRRPGCE.NEW,  38 of the prefix are found out
        # of total 57 lumps
        if leftpart.count(v) > 16:
            return v
    return None

def lumpname_ok (name):
    "Return False for corrupted or non canonical lump names, True otherwise."
    import re
    if len (name) > 50:
        return False
    else:
        m = re.match ('[A-Za-z0-9~._-]+', name)
        if m == None or m.end() != (len (name)):
            return False
    return True

def lumpnames_dont_collide (names):
    if len (names) > len (set([v.lower() for v in names])):
        return False
    return True

def read_lumplist (f):
    lumplist = []
    lumpmap = {}
    while True:
        filename, offset, size = read_lumpheader (f)
        if not filename:
            return lumplist, lumpmap
        if not lumpname_ok (filename):
            raise CorruptionError ('corrupted or non canonical lump name %r' % filename)
        lumpmap[filename.lower()] = (offset, size)
        lumplist.append (filename.lower())
        f.seek (offset + size)

class Passcode (object):
    """OHRRPGCE passcode container.
    Supports direct assignment and equality testing.

    Requires a valid GEN lump as input (probably a memmap.)
    Changing the password via Password object will be mirrored to the GEN
    data.

    Raises ValueError if a non-v256 password is detected.
    """
    __slots__ = ('_current','_gen')
    def __init__ (self, gen):
        self._current = -1
        self._gen = gen
        # detect version
        if gen.password_version < 256:
            raise ValueError ('refusing to decode old-style password.')
        if gen.password_version > 256:
            raise NotImplementedError
        self.get ()

    def get (self):
        if self._current == -1:
            rotator = self._gen.password3_rotator
            chars = []
            for char in self._gen.password3_data[0][:]:
                char = char - rotator
                if char < 0:
                    char += 255
                if char >= 32:
                    chars.append (chr (char))
            self._current = "".join(chars)
        return self._current
    def set (self, new_password):
        import random
        rotator = random.randint (1,254)
        res = []
        if new_password not in ('',None):
            for char in new_password:
                char = ord (char)
                char += rotator
                char %= rotator
                res.append (char)
        while len(res) < 17:
            blank = random.randint (1,30) + rotator
            blank %= 255
            res.append (blank)
        self._gen.password3_rotator = rotator
        self._gen.password3_data = res
        self._current = new_password
    def __str__ (self):
        return self._current
    def __eq__ (self, y):
        return self._current == y

class attackWrapper (object):
    """Pretend to be a whole attack memmap"""
    pass
