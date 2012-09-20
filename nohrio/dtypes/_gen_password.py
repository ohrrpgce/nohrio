import numpy as np
from bits import Bitsets, AttrStore

def pw4hash (password):
    """Return the 9-bit hash of `password`.

    Empty passwords hash to 0.
    """
    if not password:
        return 0
    hash = 0
    for char in password:
        hash = hash * 3 + ord(char) * 31
    return (hash & 511) | 512

def set_pw4(self, new_password):
    self.version = 4
    self.hash = pw4hash (new_password)

def get_pw4(self):
    return self.hash # as close as you get to the actual password :)

# code adapted from old nohrio.lump module.

def get_pw3(self):
    rotator = self.rotator
    chars = []
    for char in self.passcode[:]:
        char = char - rotator
        if char < 0:
            char += 255
        if char >= 32:
            chars.append (chr (char))
    return "".join(chars)

def set_pw3(self, new_password):
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
    self.version = 3
    self.rotator = rotator
    self.passcode = bytes(res)

def get_pw2(self):
    """Decode a PW2 format password.

    See `http://rpg.hamsterrepublic.com/ohrrpgce/GEN#PW2 The wiki`
    for a diagram.

    """
    offset = self.offset
    nbytes, remaining = divmod(self.length + 1, 8)
    if remaining:
        raise ValueError ('Number of bits %d in PW2 password not divisible by 8!' % (self.length+1))
    table = self.sctable
    bittable = Bitsets(table.view('B'))
    chars = []
    tableoffset = 1
    for byte in range(nbytes):
        thisval = 0
        for bit in range(8):
            thisval |= (1 if bittable[table[tableoffset]] else 0) << bit
            tableoffset += 1
        # equivalent to 'subtract offset, if result < 0 then add 256'
        rotated = (thisval - offset) % 256
        chars.append(chr(thisval))
    return ''.join(chars)

def set_pw2(self, newpassword):
    import random
    def choosebit(b, maxbit, state):
        chosen = random.randint(0, maxbit)
        state = 1 if state else 0
        while b[chosen] != state:
            chosen = random.randint(0, maxbit)
        return chosen
    offset = random.randint (1,254)
    chars = []
    for char in newpassword:
        rotated = (ord(char) + offset) % 256
        chars.append(chr(rotated))
    table = np.empty(161, dtype = 'h')
    table[0] = random.randint (1,254)
    bittable = Bitsets(table.view('B'))
    tableoffset = 1
    maxbitref = (16 * tableoffset) - 1
    for char in chars:
        byte = int(char)
        for bitindex in range(8):
            thisbit = 1 if (byte & (1 << bitindex)) else 0
            thispointer = choosebit (bittable, maxbitref, thisbit)
            table[tableoffset] = thispointer
            tableoffset += 1
            maxbitref += 16
    self.offset = offset
    self.length = len(newpassword) - 1
    self.scattertable = table

_GETSET_FUNCS = {4: (get_pw4, set_pw4),
                 3: (get_pw3, set_pw3),
                 2: (get_pw2, set_pw2),
                 }

#XXX should be a class inheriting from AttrStore

class PasswordStore (object):
    """Store OHRRPGCE RPG password info"""
    fields = ()
    def __init__ (self, gen):
        """Transfer data from GEN array into an attribute store.
        Add get(), check() and set() methods to it.
        """
        self._rawversion = gen['passcodeversion']
        V = self.version
        if V == 4:
            self.hash = gen['passwordhash']
            self.fields = ('hash',)
        elif V == 3:
            self.rotator = gen['pw3rotator']
            self.passcode = bytes(gen['pw3passcode'].view('B'))
            self.fields = tuple('rotator passcode'.split())
        else:
            self.offset = gen['pw2offset']
            self.length = gen['pw2length']
            self.sctable = gen['pw2scattertable'].view('h').copy()
            self.fields = tuple('offset length scattertable'.split())

    def copyto(self, gen):
        V = self.version
        gen['version'] = self._rawversion
        if V == 4:
            gen['passwordhash'] = self.hash
            return
        else:
            attr2numpy(self, gen, {k:'pw%d%s' % (V, k) for k in self.fields})

    def check(self, inputpwd, *, version=None):
        """Return True if inputpwd matches stored password."""
        version = version or self.version
        if version == 4:
            inputpwd = pw4hash(inputpwd)
        return self.get(version=version) == inputpwd

    def get(self, *, version=None):
        """Return the expected password -- or a hash of it."""
        version = version or self.version
        expected = _GETSET_FUNCS[self.version][0](self)
        return expected

    def set(self, inputpwd, *, version=None):
        """Set password, according to self.version.
        """
        version = version or self.version
        # wipe any attributes belonging to earlier versions
        for k in dir(self):
            if k in ('hash','rotator','passcode','offset','length','sctable'):
                delattr(self, k)
        _GETSET_FUNCS[self.version][1](self, inputpwd)

    def _get_version(self):
        rawv = self._rawversion
        if rawv < 256:
            if rawv < 3:
                raise ValueError ('Ancient PW1-style password not supported!')
            return 2
        else:
            if rawv > 257:
                raise ValueError ('password rawversion %d unknown' % rawv)
            return (3 + (rawv - 256))
    def _set_version(self, nicev):
        if nicev not in (2,3,4):
            raise ValueError('Password version %d not supported!' % nicev)
        self._rawversion = {2:255, # guessing at pw2 value.
                            3:256,
                            4:257}[nicev]
    version = property(_get_version, _set_version, doc='Simplified password version. One of (2,3,4)')


    # XXX should be done by subclassing Transferable or similar.
    def __repr__(self):
        return repr(AttrStore(**{k:getattr(self, k) for k in self.fields}))

LATEST_PASSWORD_VERSION = max(_GETSET_FUNCS.keys())