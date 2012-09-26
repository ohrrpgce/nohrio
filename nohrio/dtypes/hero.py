from bits.enum import Enum, MultiRange
from bits import attr2numpy, numpy2attr, AttrStore, UnwrappingArray, showbitsets
from bits.dtype import DType
from bitstring import BitArray
from nohrio.dtypes.common import statranges, spelllist, PalettedPic, _statlist
from nohrio.iohelpers import IOHandler
import re
import numpy as np

class SpellListType(Enum):
    map = {0: 'MP based', 1: 'FF1 LevelMP based', 2: 'Random',
           3: 'Reserved for item consuming spells'}
    valid = MultiRange(((0,3)))


#[[[cog
# import cog
# _BITSETS = ["rename when added to party",
#            "permit renaming on status screen",
#            "don't show spell lists if empty"]
# cog.outl("_BITSETS = [")
# for type in ('WEAK','STRONG','ABSORBS'):
#     for elem in range(8):
#         cog.outl('    %r,' % ('_OLD%s_E%d' % (type, elem)))
# for b in _BITSETS:
#     cog.outl('    %r,' % b)
# for v in range(27,47+1):
#     cog.outl('    \'_UNUSED%d\',' % v)
# cog.outl(']')
#]]]
_BITSETS = [
    '_OLDWEAK_E0',
    '_OLDWEAK_E1',
    '_OLDWEAK_E2',
    '_OLDWEAK_E3',
    '_OLDWEAK_E4',
    '_OLDWEAK_E5',
    '_OLDWEAK_E6',
    '_OLDWEAK_E7',
    '_OLDSTRONG_E0',
    '_OLDSTRONG_E1',
    '_OLDSTRONG_E2',
    '_OLDSTRONG_E3',
    '_OLDSTRONG_E4',
    '_OLDSTRONG_E5',
    '_OLDSTRONG_E6',
    '_OLDSTRONG_E7',
    '_OLDABSORBS_E0',
    '_OLDABSORBS_E1',
    '_OLDABSORBS_E2',
    '_OLDABSORBS_E3',
    '_OLDABSORBS_E4',
    '_OLDABSORBS_E5',
    '_OLDABSORBS_E6',
    '_OLDABSORBS_E7',
    'rename when added to party',
    'permit renaming on status screen',
    "don't show spell lists if empty",
    '_UNUSED27',
    '_UNUSED28',
    '_UNUSED29',
    '_UNUSED30',
    '_UNUSED31',
    '_UNUSED32',
    '_UNUSED33',
    '_UNUSED34',
    '_UNUSED35',
    '_UNUSED36',
    '_UNUSED37',
    '_UNUSED38',
    '_UNUSED39',
    '_UNUSED40',
    '_UNUSED41',
    '_UNUSED42',
    '_UNUSED43',
    '_UNUSED44',
    '_UNUSED45',
    '_UNUSED46',
    '_UNUSED47',
]
#[[[end]]] (checksum: 3fab188c1d29bcd694534a0bb44a622a)

DTYPE = DType("""<T{{<h:length:16h:data:}}:name:
               h:battlepic: h:battlepal: h:walkpic: h:walkpal:
               h:defaultlevel: h:defaultweapon:
               T{{{stats}}}:stats:
               4T{{{spells}}}:spells:
               h:portraitpic: 6B:bitsets:
               4T{{h:length:10h:data:}}:spelllist_name:
               h:portraitpal:
               4h:spelllist_type:
               T{{h:have:h:alive:h:leader:h:active:}}:tagsets:
               h:maxnamelength:
               2T{{h:x:h:y:}}:handcoords:
               64f:elemdmg:""".replace('\n','').replace(' ','').format(
                                stats = statranges, spells = spelllist))


MARSHALLING = """
name : readstr($name)
vis :
  battle : PalettedPic($battlepic, $battlepal)
  walk : PalettedPic($walkpic, $walkpal)
  portrait : PalettedPic($portraitpic, $portraitpal)
  handcoords : list($handcoords)
stats : {k: $stats[i] for i,v in enumerate(nohrio.dtypes.common._statlist)}




"""

_VIS = 'battle walk portrait'.split()
_ATTRMAP = {
    'name': 'name',
    'defaultlevel': 'defaultlevel',
    'defaultweapon': 'defaultweapon',
}

def readstr(data):
    #print ('DATA', data)
    #print ('trying to read {0}'.format(data))
    length = data[0]
    s = [chr(data[1][v]) for v in range(length)]
    return ''.join(s)

def prepstr(data, maxlen):
    length = len(data)
    content = [ord(c) for c in data]
    content += [0] * (maxlen - length)
    return length, content




class HeroData(IOHandler):
    dtype = DTYPE.freeze()
    def __init__(self, source):
        d = self
        # arr['name'] -> a_name
        sarr = np.fromfile(source, dtype=d.dtype, count = 1).reshape(())
        s = sarr.view(UnwrappingArray)
        #arr = UnwrappingArray(l1).reshape(())
        d.name = readstr(s['name'])
        d.vis = AttrStore(**{v: PalettedPic(s[v+'pic'],s[v+'pal'])
                                for v in _VIS})
        d.vis.handcoords = [s['handcoords'][v] for v in range(2)]
        d.stats = AttrStore(**{v:
                                 AttrStore(initial=s['stats'][i][0],
                                           final=s['stats'][i][1])
                                           for i,v in enumerate(_statlist)})
        d.tags = AttrStore()
        numpy2attr(sarr['tagsets'], d.tags)
        d.spelllist = [AttrStore(name=readstr(s['spelllist_name'][v]),
                                   attack=list(s['spells'][v]['f0'][w]['attack'] for w in range(24)),
                                   level=list(s['spells'][v]['f0'][w]['level'] for w in range(24)),
                                   type=SpellListType(s['spelllist_type'][v]))
                          for v in range(4)]
        d.elemdamage = s['elemdmg'].tolist()
        d.bitsets = BitArray(bytes=s['bitsets'])
        d.bitsets.byteswap()
        d.bitsets.reverse()

    def save(self, fh):
        from copy import deepcopy
        arr = np.zeros(1, dtype=self.dtype).reshape(())
        bitsets = deepcopy(self.bitsets)
        bitsets.reverse()
        bitsets.byteswap()
        for v in _VIS:
            pic, pal = getattr(self.vis, v)
            arr[v+'pic'] = pic
            arr[v+'pal'] = pal
        arr['elemdmg'] = self.elemdamage
        arr['bitsets'] = list(bitsets.bytes)
        nlen, n = prepstr(self.name, 16)
        arr['name']['length'] = nlen
        arr['name']['data'] = n
        print ('set name to:', arr['name'])
        arr.tofile(fh)


def load(cls, fh):
    pass

class BinsizingFH(object):
    def __init__(self, wrapped, padto):
        self.wrapped = wrapped
        self.dataread = 0
        self.padto = padto
    def read(self, amount=-1):
        if self.dataread >= self.padto:
            return ''
        tmp = self.wrapped.read(amount)
        if amount != -1:
            diff = amount - len(tmp)
            if diff:
                tmp = tmp + (b'\x00' * diff)
        else:
            diff = self.padto - self.dataread
            if diff:
                tmp = tmp + (b'\x00' * diff)
        self.dataread += len(tmp)
        return tmp


with open('../../ohrrpgce/vikings/vikings.rpgdir/viking.dt0', 'rb') as fh:
    fh.seek(HeroData.dtype.itemsize*1)
    foo = HeroData(fh)
    for k in dir(foo):
        if k.startswith('_') or callable(getattr(foo,k)) or k == 'dtype':
            continue
        print("%s:\t%r" % (k, getattr(foo, k)))
    #print(foo.name)
    #print(foo.vis.handcoords)
    showbitsets(foo.bitsets, _BITSETS)
    oldbitsets = foo.bitsets
    with open('/tmp/herodata.dt0','wb') as fh2:
        foo.save(fh2)
        print ('saving %r' % foo.name)
    with open('/tmp/herodata.dt0','rb') as fh2:
        foo2 = HeroData(fh2)
        newbitsets = foo2.bitsets
        print (oldbitsets == newbitsets)
        print (foo.name == foo2.name)
        print (foo.elemdamage == foo2.elemdamage)
