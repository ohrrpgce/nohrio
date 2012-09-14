#coding=utf8
from bits.dtype import DType, limited, enum, bitsets, OFFSET
from nohrio.dtypes.bload import bsave
from nohrio.iohelpers import FilenameOrHandleOpen, LumpOrHandleOpen, IOHandler
import numpy as np
#from bits import pep3118_dtype

# NOTE: DTYPE moved to bottom of module, cause it's huge.

# PW4 hashing
#
# HURRAH AN EASILY IMPLEMENTED AND REASONABLY SECURE PASSWORD SCHEME!

def _passwordhash (p):
    if len(p) == 0:
        return 0
    hash = 0
    for char in p:
        hash = hash * 3 + ord(char) * 31
    return (hash & 511) | 512

def set_passwordhash (gen, pwd):
    gen.passcodeversion = 4
    if pwd:
        gen.passwordhash = _passwordhash (pwd)
    else:
        gen.passwordhash = 0

def _notimplemented (gen, pwd):
    raise NotImplemented ('Password format #%d' % gen.passcodeversion)

def check_password (general, password):
    """Check the password given against the password/hash stored in the GEN lump.

    Automatically determines password version and reads the right fields.

    If there isn't a password on the RPG file, will always return True.
    """
    map = {
        1: None, # XXX feel free to implement decoders for these.
        2: None,
        3: None,
        4: lambda gen, pwd: (_passwordhash (pwd) == gen.passwordhash) if gen.passwordhash != 0 else True,
        }
    version = gen.passcodeversion
    if version not in map:
        raise ValueError ('unknown password format #%d' % version)
    if map[version] == None:
        raise NotImplemented ('password format version #%d' % version)
    return map[version] (general, password)

def set_password (general, password, version=4):
    """Set the password to `password` using the specified format (default is the latest, #4)
    """
    map = {
        1: None, # XXX feel free to implement encoders for these.
        2: None,
        3: None,
        4: set_passwordhash,
        }
    if version not in map:
        raise ValueError ('unknown password format #%d' % version)
    if map[version] == None:
        raise NotImplemented ('password format version #%d' % version)
    map[version] (general, password)

#yeah, it's a dissertation even in this format.

# at the top here, I've given a sample of an interleaved format:
#

INTERLEAVED_SAMPLE = """<h
maxmap^me

hhhh
titlebg^f titlemusic^f victorymusic^f battlemusic^f


hh17B
passcodeversion^e pw3rotator^o pw3passcode^o

x
wasted

10h
pw1password^o

"""

# YAY DECORATORS
#_save = typechecked(DTYPE, bload_saver (expectedsize = 1000))
#@array_saver
#def _save (arr, f):
    #if arr.dtype != DTYPE.freeze():
        #raise ValueError ('Dtype mismatch: can\'t save array of non-%r dtype' % __name__)

DTYPE = DType ("""
<h:maxmap^me:

h:titlebg^f:h:titlemusic^f:h:victorymusic^f:h:battlemusic^f:

h:passcodeversion^e:h:pw3rotator^o:17B:pw3passcode^o:
x:wasted:
10h:pw1password^o:

h:maxherogfx^mex:
h:maxenemy1gfx^mex:
h:maxenemy2gfx^mex:
h:maxenemy3gfx^mex:
h:maxnpcgfx^mex:
h:maxweapongfx^mex:
h:maxattackgfx^mex:
h:maxtilesetgfx^mex:

h:maxattack^me:
h:maxhero^me:
h:maxenemy^me:
h:maxformation^me:
h:maxpalette^mex:
h:maxtextbox^m:

h:nplotscripts^ms:
h:newgamescript^s:
h:gameoverscript^s:
h:maxregularscript^mes:

 H:suspendbits^g:
h:cameramode^g:
4h:cameraarg^g:
h:curbackdrop^gx:
 4h:playtime^g:

h:maxveh^me:
h:maxtagname^me:

h:loadgamescript^s:
h:curtextboxbackdrop^gx:
h:defaultenemydissolve^x:
h:usejoystick^g:

h:poisonchar^x:
h:stunchar^x:
h:damagecap^M:
h:mutechar^x:
T{h:hp:h:mp:h:atk:h:aim:h:def:h:dog:h:mag:h:wil:h:spd:h:ctr:h:focus:h:xhits:}:statcaps:

h:maxsfx^mef:
h:masterpalette^x:h:maxmasterpalette^mex:
h:maxmenu^m:h:maxmenuitem^m:
h:maxitem^m:
h:maxboxbordergfx^mx:
h:maxportraitgfx^mx:
h:maxinventory^M:

h:errorlevel:
h:levelcap^M:
h:equipmergeformula:
h:numelements^M:
h:unlockedreservexp:h:lockedreservexp:

h:passwordhash^e:
h:pw2offset^eo:h:pw2length^eo:

h:formatversion:
h:startmoney:
h:maxshop^me:

h:pw1offset^eo:
h:pw1length^eo:

h:maxbackdrop^mx:
H:bitsets:
h:startx:h:starty:h:startmap:
h:onetimenpcindexer^e:130B:onetimenpcplaceholder^e:

h:defaultdeathsfx^f:
h:maxsong^ef:
h:acceptsfx^f:
h:cancelsfx^f:
h:choosesfx^f:
h:textboxlettersfx^f:
I:bitsets2:
h:itemlearnsfx^f:h:cantlearnsfx^f:
h:buysfx^f:h:hiresfx^f:h:sellsfx^f:
h:cantsellsfx^f:h:cantbuysfx^f:

h:damagedisplayticks:h:damagedisplayrise:
h:heroweakhp:h:enemyweakhp:
h:autosortscheme:

 h:maxlevel^M:

7h:unused2:

h:pw2scattertablehead^eo:160h:pw2scattertable^eo:

140h:unused3:
""".replace('\n','').replace(' ',''),
    suspendbits = bitsets ('npcs player obstruction herowalls npcwalls caterpillar'
                           ' randomenemies boxadvance overlay ambientmusic'),
    maxlevel = limited (99), # start, stop, [individualitems]
    playtime = DType ('h:days:h:hours:h:minutes:h:seconds:',
                      hours = limited (23),
                      minutes = limited (59),
                      seconds = limited (59)),
    e = 'editoronly',
    f = 'sound',
    g = 'gameonly',
    m = 'max',
    M = 'softmax',
    o = 'obsolete',
    x = 'gfx',)

# TODO: make a general ndarray subclass for nohrio array types to derive from

class GeneralData (IOHandler,np.ndarray):
    def _save (self, fh):
        bsave (self, fh)
    def _load (self, fh):
        tmp = np.frombuffer(bload (fh), DTYPE)
        self[:] = tmp[:]
        return self

#print (DTYPE['autosortscheme'][OFFSET])
# XXX enum-ize defaultenemydissolve, errorlevel, equipmergeformula, autosortscheme
# XXX bitset-ize bitsets and bitsets2
# XXX limits on various things
# XXX some grouping missing.


__ALL__ = ('general', 'check_password', 'set_password', 'DTYPE')
