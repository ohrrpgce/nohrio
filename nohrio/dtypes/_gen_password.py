# Hit list:
#
#  PW4 X
#  PW3 X
#  PW2

def pw4hash (p):
    if not p:
        return 0
    hash = 0
    for char in p:
        hash = hash * 3 + ord(char) * 31
    return (hash & 511) | 512

def set_pw4(self, new_password):
    self.version = 4
    self.hash = pw4hash (new_password)

def get_pw4(self):
    return self.hash # as close as you get to the actual password :)

# code adapted from old nohrio.lump module.

def get_pw3(self)
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
    raise NotImplementedError()

def set_pw2(self, new_password):
    raise NotImplementedError()


_GETSET_FUNCS = {4: (get_pw4, set_pw4),
                 3: (get_pw3, set_pw3),
                 2: (get_pw2, set_pw2),
                 }

def init_passdata (gen, passobj):
    """Transfer data from GEN array into an attribute store.
    Add get(), check() and set() methods to it.
    """
    passobj.rawversion = gen['passcodeversion']
    if passobj.rawversion < 256:
        if passobj.rawversion < 3:
            raise ValueError ('Ancient PW1-style password not supported!')
        passobj.version = 2
    else:
        if passobj.rawversion > 257:
            raise ValueError ('password rawversion %d unknown' % passobj.rawversion)
        passobj.version = 3 + (passobj.rawversion - 256)
    V = passobj.version
    if V == 4:
        passobj.hash = gen['passwordhash']
    elif V == 3:
        passobj.rotator = gen['pw3rotator']
        passobj.passcode = bytes(gen['pw3passcode'].view('B'))
    else:
        passobj.offset = gen['pw2offset']
        passobj.length = gen['pw2length']
        passobj.sctable = bytes(gen['pw2scattertable'].view('B'))

    def check(inputpwd):
        """Return True if inputpwd matches stored password."""
        if passobj.version == 4:
            inputpwd = pw4hash(inputpwd)
        return passobj.get() == inputpwd

    def get():
        """Return the expected password -- or a hash of it."""
        expected = _GETSET_FUNCS[passobj.version][0](passobj)
        return expected

    def set(inputpwd):
        """Set password, according to passobj.version.
        """
        # wipe any attributes belonging to earlier versions
        for k in dir(passobj):
            if k in ('hash','rotator','passcode','offset','length','sctable'):
                delattr(passobj, k)
        _GETSET_FUNCS[passobj.version][1](passobj, inputpwd)
    # ZE MAGICKS!
    passobj.check = check
    passobj.set = set
    passobj.get = get



