from bitstring import BitArray
from bits import bitsetsfromlebytes, lebytesfrombitsets
from nohrio.iohelpers import IOHandler, Filelike

#[[[cog
# import cog
# import re, os
# rex = re.compile ('CONST fix([a-zA-Z0-9]+) += +([0-9]+)')
# wordrex = re.compile ('[A-Z]+[a-z0-9]+')
# cog.outl('fixbits_names = [')
# info = []
# with open(os.path.expanduser('../../ohrrpgce/const.bi'),'r') as f:
#     for line in f:
#         m = rex.match(line)
#         if not m:
#             continue
#         name, id = m.groups()
#         id = int(id)
#         if not name.isupper(): # UNUSED23
#             if name == 'Attackitems':
#                 name = 'AttackItems'
#             parts = wordrex.findall(name)
#             name = "_".join([v.lower() for v in parts])
#         info.append((id, name))
# info.sort (key = lambda v: v[0])
# # add 8 bits of padding to show up unknown new bitsets
# info.extend((v, 'UNKNOWN%d' % v) for v in range(len(info), len(info)+8))
# for id, name in info:
#     cog.outl('    %r,' % name)
#
# cog.outl('    ]')
# cog.outl('fixbits_nbytes = %d' % ((info[-1][0] + 8) / 8))
#]]]
fixbits_names = [
    'attack_items',
    'weap_points',
    'stun_cancel_targ',
    'default_dissolve',
    'default_dissolve_enemy',
    'push_npcbug_compat',
    'default_max_item',
    'blank_door_links',
    'shop_sounds',
    'extended_npcs',
    'hero_portrait',
    'text_box_portrait',
    'npclocation_format',
    'init_damage_display',
    'default_level_cap',
    'hero_elementals',
    'old_elemental_fail_bit',
    'attack_element_fails',
    'enemy_elementals',
    'item_elementals',
    'num_elements',
    'remove_damage',
    'default_max_level',
    'UNUSED23',
    'UNKNOWN24',
    'UNKNOWN25',
    'UNKNOWN26',
    'UNKNOWN27',
    'UNKNOWN28',
    'UNKNOWN29',
    'UNKNOWN30',
    'UNKNOWN31',
    ]
fixbits_nbytes = 4
#[[[end]]] (checksum: b41bf88f4b4a9a9f18447eb63f53d565)

class FixBits(BitArray,IOHandler):
    def __init__(self, *args, source=None, **kwargs):
        """Accepts a filename/handle as initializer (via 'source' kwarg)
        """
        pass

    def __new__(cls, *args, source=None, **kwargs):
        if not source:
            return BitArray.__new__(cls, *args, **kwargs)

        tmp=None
        with Filelike(source, 'rb') as fh:
            tmp = bitsetsfromlebytes(cls, fh.read())
        return tmp

    def __str__(self):
        return '%s(0x%s,%r)' % (self.__class__.__name__,
                              self.hex,
                           ' '.join(fixbits_names[i] for i,v in enumerate(self) if v))
    def _save(self, fh):
        bytes = lebytesfrombitsets(self)
        fh.write(bytes)

    def __getitem__(self, k):
        if type(k) == str:
            return BitArray.__getitem__(self, fixbits_names.index(k))
        return BitArray.__getitem__(self, k)
    # that's it!
def _load(cls, fh):
    return cls(source=fh)
FixBits._load = _load.__get__(FixBits)
#f = FixBits(uint = int('10'*12,2), length = 24)
#print (str(f))
#f = FixBits(source = '../../ohrrpgce/vikings/vikings.rpgdir/fixbits.bin')
#print (f.bin)
#print (str(f))
#print ([hex(v) for v in lebytesfrombitsets(f)])
