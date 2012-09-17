#coding=utf8
from bits.dtype import DType, limited, enum, bitsets, OFFSET
from nohrio.dtypes.bload import bsave, bload
from nohrio.iohelpers import Filelike, FilelikeLump, IOHandler
from nohrio.objutil import AttrStore
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

 2B:suspendbits^g:
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
# XXX: how do I modify which classes I'm subclassing?
#      Needed for array2attr.
#      .. I don't. instead, use type() to construct a new class.
#      cf http://stackoverflow.com/questions/2783974/adding-inheritance-to-a-class-programmatically-in-python
#      except really, I should only need to construct it once.
#
#
#      What about this:
#      I don't really need to use classes for this. A simple named-tuple
#      (save = foo, load = bar, output_formats = ('array',),data = {some:stuff}) describes most everything.
#      Classes can then be generated from that IF NEED BE.


def consume (seq):
    """Yield seq, receive a set of 'consumed items', remove them from seq,
       yield the revised seq,... until no items of seq are left, or none
       are removed.
    """
    seq = list(seq)
    nremoved = 0xfffffff
    while seq and nremoved:
        consumed = (yield seq)
        nremoved = 0
        for v in consumed:
            seq.remove(v)
            nremoved += 1

def numpy2attr (src, dest, attrmap):
    """Copy numpy array fields to instance/class attributes semi-intelligently.
    """
    used = set ()
    for field, destfield in attrmap.items():
        if destfield in used:
            raise ValueError('>1 instance of attribute name %s' % destfield)
        used.add(destfield)
        try:
            tmp = src[field].item()
        except ValueError:
            tmp = src[field].squeeze().tolist()
        try:
            # convert np.void -> list
            if len(tmp):
                tmp = list(tmp)
        except:
            pass
        setattr(dest, destfield, tmp )

#[[[cog
#import cog
#]]]
#[[[end]]]

def shorten(shared, v):
    return (v if not (v.startswith(shared) or v.endswith(shared)) else v.replace(shared,''))

_ATTRMAP = {'cap': {'damagecap': 'damage',
             'levelcap':        'level',
             'numelements':     'numelements',
             'statcaps':        'stats'},
     #'formatversion': 'formatversion',
     'max': {'maxattack':    'attack',
             'maxattackgfx': 'attackgfx',
             'maxbackdrop':  'backdrop',
             'maxboxbordergfx': 'boxbordergfx',
             'maxenemy':        'enemy',
             'maxenemy1gfx':    'enemy1gfx',
             'maxenemy2gfx':    'enemy2gfx',
             'maxenemy3gfx':    'enemy3gfx',
             'maxformation':    'formation',
             'maxhero':         'hero',
             'maxherogfx':      'herogfx',
             'maxinventory':    'inventory',
             'maxitem':         'item',
             'maxlevel':        'level',
             'maxmap':          'map',
             'maxmasterpalette': 'masterpalette',
             'maxmenu':         'menu',
             'maxmenuitem':     'menuitem',
             'maxnpcgfx':       'npcgfx',
             'maxpalette':      'palette',
             'maxportraitgfx':  'portraitgfx',
             'maxregularscript': 'regularscript',
             'maxsfx':         'sfx',
             'maxshop':        'shop',
             'maxsong':        'song',
             'maxtagname':     'tagname',
             'maxtextbox':     'textbox',
             'maxtilesetgfx':  'tilesetgfx',
             'maxveh':         'veh',
             'maxweapongfx':   'weapongfx'},
     'misc': {'autosortscheme': 'autosortscheme',
# manually merged into one object
#              'bitsets': 'bitsets',
#              'bitsets2': 'bitsets2',
              'damagedisplayrise':    'damagedisplayrise',
              'damagedisplayticks':   'damagedisplayticks',
              'defaultenemydissolve': 'defaultenemydissolve',
              'enemyweakhp':       'enemyweakhp',
              'equipmergeformula': 'equipmergeformula',
              'errorlevel':      'errorlevel',
              'heroweakhp':      'heroweakhp',
              'lockedreservexp': 'lockedreservexp',
              'masterpalette':   'masterpalette',
              'mutechar':   'mutechar',
              'poisonchar': 'poisonchar',
              'stunchar':   'stunchar',
              'titlebg':    'titlebg',
              'unlockedreservexp': 'unlockedreservexp'},
     'password': {'passcodeversion': 'version',
# only some of these are copied, manually, according to determination of the password format version.
#              'passwordhash': 'passwordhash',
#              'pw1length': 'pw1length',
#              'pw1offset': 'pw1offset',
#              'pw1password': 'pw1password',
#              'pw2length': 'pw2length',
#              'pw2offset': 'pw2offset',
#              'pw2scattertable': 'pw2scattertable',
#              'pw2scattertablehead': 'pw2scattertablehead',
#              'pw3passcode': 'pw3passcode',
#              'pw3rotator': 'pw3rotator'
              },
     'runtime': {'cameraarg':    'cameraarg',
                 'cameramode':  'cameramode',
                 'curbackdrop': 'curbackdrop',
                 'curtextboxbackdrop': 'curtextboxbackdrop',
                 'onetimenpcindexer':  'onetimenpcindexer',
                 'onetimenpcplaceholder': 'onetimenpcplaceholder',
                 'playtime':      'playtime',
                 'suspendbits':   'suspendbits',
                 'usejoystick':   'usejoystick'},
     'script': {'gameoverscript': 'gameover',
                'loadgamescript': 'loadgame',
                'newgamescript':  'newgame',
                'nplotscripts':   'nplotscripts'},
     'sound': {'acceptsfx':   'accept',
               'battlemusic': 'battlemusic',
               'buysfx':      'buy',
               'cancelsfx':   'cancel',
               'cantbuysfx':  'cantbuy',
               'cantlearnsfx': 'cantlearn',
               'cantsellsfx': 'cantsell',
               'choosesfx':   'choose',
               'defaultdeathsfx': 'defaultdeath',
               'hiresfx':     'hire',
               'itemlearnsfx': 'itemlearn',
               'sellsfx':     'sell',
               'textboxlettersfx': 'textboxletter',
               'titlemusic':  'titlemusic',
               'victorymusic': 'victorymusic'},
     'start': {'startmap':   'map',
               'startmoney': 'money',
               'startx':     'x',
               'starty':     'y'},
     'unused': {'unused2': 'two', 'unused3': 'three', 'wasted': 'one'}}

#_CATEGORYMAP = {
#                'misc': {v:v for v in 'stunchar poisonchar mutechar defaultenemydissolve bitsets bitsets2 errorlevel unlockedreservexp #heroweakhp lockedreservexp damagedisplayrise enemyweakhp masterpalette damagedisplayticks equipmergeformula titlebg autosortscheme'.split(' ')},
#                'max' : {v:shorten('max', v) for v in DTYPE.names() if 'max' in v},
#                'sound' : {v:shorten('sfx', v) for v in DTYPE.names() if 'max' not in v and 'sfx' in v or 'music' in v},
#                'script' : {v:shorten('script', v) for v in DTYPE.names() if 'max' not in v and 'script' in v},
#                'unused' : {v:'_%d' % (i+1) for i,v in enumerate(DTYPE.names()) if 'unused' in v or 'wasted' in v},
#                'runtime' : {v:v for v in DTYPE.names() if 'camera' in v or 'onetime' in v or 'cur' in v},
#                'pass' : {v:v for v in DTYPE.names() if 'pass' in v or 'pw' in v},
#                'cap' : {v:shorten('cap',v) for v in DTYPE.names() if 'cap' in v or 'numelem' in v},
#                'start' : {v:shorten('start',v) for v in DTYPE.names() if 'start' in v or 'pw' in v},
#                'formatversion': 'formatversion',
#                }
#_CATEGORYMAP['runtime'].update({v:v for v in 'playtime usejoystick suspendbits'.split(' ')})
#_CATEGORYMAP['init'].update({v:v for v in })
#seen = set()
#for k,v in _CATEGORYMAP.items():
#    if type(v) != dict:
#        seen.add(k)
#        continue
#    this = set(v.keys())
#    shared = seen.intersection(this)
#    if shared:
#        print ('SHARED! %r' % shared)
#    seen.update(this)

#import pprint
#pprint.pprint(_CATEGORYMAP)


#def prefilter (dtype):
#    names = dtype.names()
#    #remove preassigned from consideration
#    for k,v in _CATEGORYMAP.items():
#        for k2 in v:
#            if k2 in names:
#                names.remove(k2)
#    consumer = consume(names)
#    remaining = consumer.send(None)
#    print (remaining)
#    for v in ('start',):
#        chosen = [name for name in remaining if v in name]
#        print ('%s chose : %s' % (v, chosen))
#        target = _CATEGORYMAP.setdefault(v, {})
#        target.update({k:k for k in chosen})
#        remaining = consumer.send(chosen)
#    del consumer
#    print ('Remaining(%d): %s' % (len(remaining), ' '.join(remaining)))

#prefilter (DTYPE)
#print ({k:len(v) for k,v in _CATEGORYMAP.items()})
#print ('n'.join

# XXX prefilter -- build category lists just the one time, so the GeneralData constructor can be much
# faster and simpler.

class GeneralData (IOHandler):
    _dtype = DTYPE
    # XXX for now, we only init from file.
    def __init__ (self, source):
        with Filelike(source, 'rb') as fh:
            #def join(fields):
            src = np.frombuffer(bload (fh, newformat_ok = True), self._dtype.freeze())
            for submap, members in _ATTRMAP.items():
                store = AttrStore()
                numpy2attr(src, store, members)
                setattr(self, submap, store)
                print ('%s: %r' % (submap, store))
            self.formatversion = src['formatversion'].item()
            print (self.formatversion)
            v = self.password.version
            self.password.present = False
            if v in (256,257):
                v = (256,257).index(v) + 3
                if v == 4:
                    self.password.hash = src['passwordhash'].item()
                    print ('current pwd hash == %s' % self.password.hash)
                    # XXX hack, this should be a separate function in the outside scope.
                    def _change(self2, newpassword):
                        self2.hash = None if not newpassword else _passwordhash(newpassword)
                        self2.present = bool(newpassword)
                    self.password.change = _change
                    self.password.check = lambda self2,inputpwd: _passwordhash(inputpwd) == self2.hash
                    self.password.present = self.password.hash != 0
                    print ('password is present: %r' % self.password.present)
                else:
                    raise NotImplementedError
            elif v >= 3:
                v = 2
                raise NotImplementedError
            else:
                v = 1
                raise NotImplementedError
            print ('I think the password version is %r' % v)

            # TODO: use bits.bitsets or the ilk.
            #       * add self.misc.bitsets = bits.bitsets(bytearray merge of bitsets and bitsets2)
            #       * change self.runtime.suspendbits to be a bits.bitsets(bytearray conversion of suspendbits)


            #if others:
            #    raise NotImplementedError('Fields[%d]: %s' % (len(others), " ".join (sorted(others))))


    def _save (self, fh):
        buf = np.zeros((),self._dtype)
        # fill in
        bsave (buf, fh)

    def _load (fh):
        __class__(fh)


    def _reloadfrom (self, fh):
        raise NotImplementedError()

#print (len(DTYPE.names()))
#_max, others = splitfilter (DTYPE.names(), lambda v: 'max' in v)
#print ([len(v) for v in (_max, others)])


g = GeneralData('../../tests/ohrrpgce.rpgdir/ohrrpgce.gen')



#def subclassish (name, *superclasses):
    #type(name,
#class GeneralData_subclasstest (IOHandler)



#print (DTYPE['autosortscheme'][OFFSET])
# XXX enum-ize defaultenemydissolve, errorlevel, equipmergeformula, autosortscheme
# XXX bitset-ize bitsets and bitsets2
# XXX limits on various things
# XXX some grouping missing.


__ALL__ = ('general', 'check_password', 'set_password', 'DTYPE')
