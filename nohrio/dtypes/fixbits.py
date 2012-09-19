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
# for id, name in info:
#     cog.outl('    %r,' % name)
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
    ]
fixbits_nbytes = 3
#[[[end]]] (checksum: 2517d7188d349cc80bbc67f298a366b8)

from bits import Bitsets
print(fixbits_names)
buffer = bytearray((0b10101010,) * fixbits_nbytes)
print('%s' % Bitsets(buffer, fixbits_names))