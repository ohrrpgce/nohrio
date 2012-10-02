#coding=utf8
from bits.dtype import DType, limited, enum, bitsets, OFFSET
from bits.enum import Enum, MultiRange
from bits import (numpy2attr, attr2numpy, UnwrappingArray, AttrStore,
                 bitsetsfromlebytes, lebytesfrombitsets, showbitsets)
#int2bitlist, bitlist2int
from nohrio.dtypes.bload import bsave, bload
from nohrio.iohelpers import Filelike, FilelikeLump, IOHandler
from bitstring import BitArray

from nohrio.dtypes.common import readstr, scalararray
from nohrio.dtypes._gen_password import PasswordStore, LATEST_PASSWORD_VERSION
import numpy as np
import struct


#[[[cog
#import cog
#cog.outl('')
#with open('../../ohrrpgce/const.bi','r') as f:
#    canexit = False
#    for line in f:
#        if line.startswith("'") and ('version history' in line.lower()):
#            cog.outl('# --- Version History ---')
#            canexit = True
#            continue
#        if canexit:
#            line = line.strip()
#            if not line:
#               break
#            cog.outl('#' + line[1:])
#cog.outl('')
#cog.outl('')
#]]]

# --- Version History ---
# 7 - ypsiliform wip added > 36 NPC defs (and many other features)
# 8 - ypsiliform wip added extended chaining data (and many other features)
# 9 - ypsiliform wip added text box sound effects
# 10 - ypsiliform wip added attack-based enemy transmogrification
# 11 - zenzizenzic wip added variable record size and record number .N## lumps
# 12 - zenzizenzic wip increased .N## record size
# 13 - zenzizenzic wip changed password format to PW4, older versions have broken genPassVersion handling
# 14 - zenzizenzic wip made .DT0 binsize-sized
# 15 - zenzizenzic wip made .DT1 binsize-sized, and added binsize.bin, fixbits.bit safeguards
# 16 - zenzizenzic wip made .ITM binsize-sized
# 17 - alectormancy wip increase global limit from 4095 to 16383


#[[[end]]] (checksum: f65a3269ba056b7c4b6279d6d90b71cf)

#yeah, it's a dissertation even in this format.

# at the top here, I've given a sample of a RST-style tabular format.
# it's intended as a format you can compile to a pretty-printed dtype()
# call, rather than a realtime thing :)
#
# ~ means default.

MINIMUM_FORMAT = 2
CURRENT_FORMAT = 17

DTYPE = DType ("""
<h:maxmap^me:

h:titlebg^f:h:titlemusic^f:h:victorymusic^f:h:battlemusic^f:

h:passcodeversion^e:h:pw3rotator^o:17B:pw3passcode^o:
B:wasted:
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

h:numbackdrops^mx:
2B:bitsets:
h:startx:h:starty:h:startmap:
h:onetimenpcindexer^e:130B:onetimenpcplaceholder^e:

h:defaultdeathsfx^f:
h:maxsong^ef:
h:acceptsfx^f:
h:cancelsfx^f:
h:choosesfx^f:
h:textboxlettersfx^f:
4B:bitsets2:
h:itemlearnsfx^f:h:cantlearnsfx^f:
h:buysfx^f:h:hiresfx^f:h:sellsfx^f:
h:cantsellsfx^f:h:cantbuysfx^f:

h:damagedisplayticks:h:damagedisplayrise:
h:heroweakhp:h:enemyweakhp:
h:autosortscheme:

 h:maxlevel^M:

7h:unused2:

161h:pw2scattertable^eo:

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
    x = 'gfx')


# XXX: how do I modify which classes I'm subclassing?
#      Needed for array2attr.
#      .. I don't. instead, use type() to construct a new class.
#      cf http://stackoverflow.com/questions/2783974/adding-inheritance-to-a-class-programmatically-in-python
#      except really, I should only need to construct it once.

_ATTRMAP = {'cap': {'damagecap': 'damage',
             'levelcap':        'level',
             'numelements':     'numelements',
             'statcaps':        'stats'},
     #'formatversion': 'formatversion',
     'max': {'maxattack':    'attack',
             'maxattackgfx': 'attackgfx',
#             'maxbackdrop':  'backdrop',
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
#     'password': {'passcodeversion': 'version',
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
#              },
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

_DOCSTRINGS = {
    'max': "Maximum (ie. == nrecords - 1) indices into multirecord lumps",
    'runtime':  "Runtime data. If you're not parsing a SAV file, ignore this.",
    'script' :  "Which scripts are run for which fixed events; and total number of scripts.",
    'unused' :  "Unused data fields. May contain useful data if the formatversion "
                "is newer than GeneralData understands.\n"
                "Written as-is when saving a GEN lump. "
                " In general it's safe to ignore this attribute.",
    'start'  :  "Where and with what the player begins the RPG",
    'sound'  :  "Sound effects and music that play at specific types of event",
    'password': "Password data. Do not access directly.\n"
                "Instead use password.check|set().\n"
                "Only stores password information for the fields "
                "relevant to the password version in use.",
    'cap'    :  "Maximums of various gameplay related values.",
    'misc'   :  "Everything else.",
               }

#[[[cog
# import cog
# import re, os
# import requests
# # there doesn't appear to be any constants for these in the source code
# # ... so we webscrape instead.
# response = requests.get('http://rpg.hamsterrepublic.com/ohrrpgce/GEN')
# content = response.content.decode('utf8')
# areas = re.findall('<td>[^<]+bitsets.+?</td>', content, re.DOTALL)
# cog.outl('# taken from %d separate fields' % len(areas))
# #rex = re.compile('<br(?: ?/)?>.+?')
# rex = re.compile ('<br(?: ?/)?>(?:\n(?:<p>)?)?([0-9]+) *- *([^<]+)')
# cog.outl('_BITSETS = [')
# index = 0
# for area in areas:
#     allfound = rex.findall(area)
#
#     for number, name in allfound:
#         name = name.partition('(')[0].strip().lower()
#         name = re.sub('([a-z])-([a-z])','\\1\\2', name)
#         name = re.sub("['.]+",'', name)
#         tmp = '    %r,' % name
#         if index % 8 == 0:
#             tmp+= '    # %d' % index
#         cog.outl(tmp)
#         index += 1
# while index < 48:
#     cog.outl("    'UNUSED%d'," % index)
#     index += 1
# cog.outl('    ]')
# cog.outl('_BITSETS.reverse()  # BitArray is big endian, OHRRPGCE is little-endian.')
#]]]
# taken from 2 separate fields
_BITSETS = [
    'pause in battle on spell and item menus',    # 0
    'enable caterpillar party',
    'dont restore hp on levelup',
    'dont restore mp on levelup',
    'inns dont revive dead heros',
    'hero swapping always available',
    'hide ready meter in battle',
    'hide health bar in battle',
    'disable debugging keys',    # 8
    'simulate old levelup bug',
    'permit doubletriggering of scripts',
    'skip title screen',
    'skip load screen',
    'pause in battle on all menus',
    'disable heros battle cursor',
    'default passability disabled by default',
    'simulate pushable npc collision bug',    # 16
    'disable esc to run from battle',
    'dont save gameover/loadgame script ids',
    'dead heroes gain share of experience',
    'locked heros cant be rearranged',
    'attack captions pause battle meters',
    'dont randomize battle readymeters',
    'battle menus wait for attack animations',
    'enable better scancodes for scripts',    # 24
    'simulate old fail vs elemental resist bit',
    '0 damage when immune to attack elements',
    'recreate map slices when changing maps',
    'harm tiles harm noncaterpillar heroes',
    'attacks ignore extra hits by default',
    'dont divide experience between heroes',
    'dont reset max stats after oob attack',
    'dont limit max tags to 1000',    # 32
    'UNUSED33',
    'UNUSED34',
    'UNUSED35',
    'UNUSED36',
    'UNUSED37',
    'UNUSED38',
    'UNUSED39',
    'UNUSED40',
    'UNUSED41',
    'UNUSED42',
    'UNUSED43',
    'UNUSED44',
    'UNUSED45',
    'UNUSED46',
    'UNUSED47',
    ]
#_BITSETS.reverse()
# [[[end]]] (checksum: 922a420558c47b66b15c7377dcf2b587)


def load(cls, fh):
    cls(fh)

class AutosortScheme(Enum):
    map = {0: 'by type', 1: 'usable/not usable',
           2: 'alphabetically', 3: 'by id number',
           4: 'compact only'}
    valid = MultiRange(((0,4),))

class BrowseInfo(IOHandler):
    """Holds author and long game name info
    """
    def __init__(self, source):
        self.longname = readstr(source, 2, 1, 38)
        self.about = readstr(source, 2, 1, 38)
    def _save(self, fh):
        writestr(self.longname, 2, 1, 38)
        writestr(self.about, 2, 1, 38)

class GeneralData(IOHandler):
    """Container for general data

    GeneralData(filehandle_or_filename)

    The data source must include the bload header.

    """
    _dtype = DTYPE.freeze()
    BITSETS = _BITSETS
    # XXX for now, we only init from file.
    def __init__ (self, source):
        print ('init from %r' % source)
        with Filelike(source, 'rb') as fh:
            # frombuffer always returns a shaped array, so we have to reshape it
            # to a scalar.
            bloaded = bload (fh, newformat_ok = True)
            if len (bloaded) != self._dtype.itemsize:
                raise ValueError('Wrong content length %d, expected %d' % (len(bloaded),
                                                                          self._dtype.itemsize))
            src = scalararray(self._dtype, data=bloaded)

            for submap, members in _ATTRMAP.items():
                store = AttrStore()
                numpy2attr(src, store, members)
                # XXX this doesn't show up on help()'s radar.
                #     Probably I should put it in the GeneralData docstring instead.
                store.__doc__ = _DOCSTRINGS[submap]
                setattr(self, submap, store)
            self.max.backdrops = src['numbackdrops'] - 1
            self.misc.autosortscheme = AutosortScheme(self.misc.autosortscheme)
            print ('autosort is set to %r' % self.misc.autosortscheme)
            #    print ('%s: %r' % (submap, store))
            self.formatversion = src['formatversion']
            if self.formatversion > CURRENT_FORMAT or self.formatversion < MINIMUM_FORMAT:
                raise ValueError
            print (self.formatversion)
            self.passinfo = PasswordStore(src)
            self.passinfo.present = bool (self.passinfo.get())
            self.misc.bitsets = bitsetsfromlebytes(BitArray,
                                                   src['bitsets'].tolist() + src['bitsets2'].tolist())
            #bittmp = int2bitlist(src['bitsets'], 16) + int2bitlist(src['bitsets2'], 32)
            #print (bin(src['bitsets']), bin(src['bitsets2']))
            #self.misc.bitsets = BitArray(bittmp)
                                         #'uint:32=%d, uintne:16=%d' % (src['bitsets2'],
                                          #                       src['bitsets']))
            print ('bitsets sez: %s' % self.misc.bitsets.bin)
            showbitsets(self.misc.bitsets, self.BITSETS)
            print ('I think the password version is %r' % self.passinfo.version)
            print ('passinfo obj: %r' % self.passinfo)
            print ('passinfo vars: %r' % vars(self.passinfo))
            print ('passinfo.get(): %r' % self.passinfo.get())

            # TODO: use bits.bitsets or the ilk.
            #       * add self.misc.bitsets = bits.bitsets(bytearray merge of bitsets and bitsets2)
            #       * change self.runtime.suspendbits to be a bits.bitsets(bytearray conversion of suspendbits)


            #if others:
            #    raise NotImplementedError('Fields[%d]: %s' % (len(others), " ".join (sorted(others))))


    def _save (self, fh):
        buf = scalararray(self._dtype)
        for submap, members in _ATTRMAP.items():
            attr2numpy (getattr(self, submap), buf, members, reversed = True)
        buf['numbackdrops'] = self.max.backdrops + 1
        buf['formatversion'] = self.formatversion
        #self.misc.bitsets.reverse()
        bytes = lebytesfrombitsets(self.misc.bitsets)
        buf['bitsets'] = bytes[:2]
        buf['bitsets2'] = bytes[2:]
        #b = self.misc.bitsets.uint
        #buf['bitsets'] = b & 0xffff
        #buf['bitsets2'] = (b >> 16) & 0xffffffff
        #self.misc.bitsets.reverse()
        self.passinfo.copyto(buf)
        bsave (buf, fh)

    #def _load (fh):
        #__class__(fh)


    def _reloadfrom (self, fh):
        raise NotImplementedError()

# XXX for bits objutil:
# bindfunc = lambda cls,f: f.__get__(cls)
GeneralData._load = load.__get__(GeneralData)

#print (len(DTYPE.names()))
#_max, others = splitfilter (DTYPE.names(), lambda v: 'max' in v)
#print ([len(v) for v in (_max, others)])


if __name__ == "__main__":
    import glob
    import sys
    import os
    rpgdir = '../../tests/ohrrpgce.rpgdir/'
    if len(sys.argv) > 1:
        rpgdir = sys.argv[1]
    genpath = glob.glob(os.path.join(rpgdir, '*.gen'))[0]
    g = GeneralData(genpath)
    g.passinfo.set('abcdefg')
    g.save('/tmp/test.gen')



#def subclassish (name, *superclasses):
    #type(name,
#class GeneralData_subclasstest (IOHandler)



#print (DTYPE['autosortscheme'][OFFSET])
# XXX enum-ize defaultenemydissolve, errorlevel, equipmergeformula, autosortscheme
# XXX bitset-ize bitsets and bitsets2
# XXX limits on various things
# XXX some grouping missing.


__ALL__ = ('general', 'check_password', 'set_password', 'DTYPE')
