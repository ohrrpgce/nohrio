from bits import Enum
from bits.dtype import DType
from nohrio.iohelpers import IOHandler, Filelike
from nohrio.dtypes.common import (PalettedPic, scalararray,
                                  readstr, writestr, copyfrom)

class Thievability(Enum):
    valid = (-1,0,1)
    map = {-1: 'never',
           0: 'once only',
           1: 'infinite'}

class DissolveType(Enum):
    valid = range(0, 11)
    map = {
            0: 'Default',
            1: 'Random pixels',
            2: 'Crossfade',
            3: 'Diagonal vanish',
            4: 'Sink into ground',
            5: 'Squash',
            6: 'Melt',
            7: 'Vapourise',
            8: 'Phase out',
            9: 'Squeeze',
            10: 'Shrink',
            11: 'Flicker'
          }

DTYPE = DType("""34B:name: h:thievability: h:stealable_item: h:stealchance:
               h:raresteal_item: h:raresteal_chance: h:dissolve: h:dissolvespeed:
               h:deathsound: 2h:battlecursor: 26h:unused: h:picture: h:palette: h:picsize: 6h:rewards: 12h:stats:
               10B:bitsets:
               T{h:death:h:nonelemdeath:h:alone:h:nonelemhit:8h:elemhit:h:amount:}:spawning:
               T{5h:regular:5h:desperation:5h:alone:8h:counterelem:12h:counterstats:56h:counterelem2:}:attacks:
               56h:elemspawn2:
               64f:elemdamage:""").freeze()

#[[[cog
# import cog
# import re, os
# import requests
# # there doesn't appear to be any constants for these in the source code
# # ... so we webscrape instead.
# response = requests.get('http://rpg.hamsterrepublic.com/ohrrpgce/DT1')
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

#[[[end]]]


class Enemy(IOHandler):
    def __init__(self, source):
        with Filelike(source, 'rb') as fh:
            src = scalararray(DTYPE, fh.read(DTYPE.itemsize))
            print(src['elemdamage'])
    def _save(self, fh):
        pass

if __name__ == "__main__":
    t = Enemy('../../ohrrpgce/vikings/vikings.rpgdir/viking.dt1')
    print(t)
