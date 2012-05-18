"""compact dtype strings (PEP3118 format)

See the OHRRPGCE wiki at http://rpg.hamsterrepublic.com/ohrrpgce/index.php for up to date versions.
"""
from bits.compactdtype import dtype, D, groups
coord = 'h:x-X coordinate:h:y-Y coordinate:'
range = 'h:min-Minimum value:h:max-Maximum value:'

# XXX you could treat the lump header as a pair of H, both big-endian.
#
lumpsize_header = 'B:b1-High byte:B:b0-Highest byte:B:b3-Lowest byte:B:b2-Low Byte:'
browse = '40s:longname:40s:about:'
binsize = 'h:attack:h:stf:h:songdata:h:sfxdata:h:map:h:menus:h:menuitem:h:uicolors:h:say:h:npc:h:dt0:h:dt1:h:itm:'
class BINSIZE(object):
    attack=60
_tagtuple = 'h:set:h:cond:h:check:'
_chainbits = '?:attackermustknowtoo:?:chainedignoresdelay:?:nonblockingdelay:?:dontretarget:<uint12:unknown:'
_chaintuple = 'h:attack:h:condtype:h:rate:2h:val:t{%_chainbits%}:bits:'
#chaintuple = 'h:attack:h:condtype:h:rate:2h:val:2B:bits:'
# XXX currently fails.
attack = ('T{h:pic^a:h:pal^a:h:pattern^a:}:anim:T{h:class^t:h:setting^t:}:target:h:damageequation:'
'h:aimmath:h:baseattackstat:T{h:mp^c:h:hp^c:h:money^c:}:cost:h:extradamage:T{h:attack:h:rate:}:chainbase:'
'h:attackeranim^a:h:attackanim^a:h:attackdelay:h:nhits:h:targetstat^st:h:preftarget^t:8B:bitsets1^b:'
'24s:name^ax:h:captiontime^a:40s:caption^ax:h:captiondelay:h:defstat^s:2T{%_tagtuple%}:tag:16B:bitsets2^b:'
'40s:description^ax:3h:consumeitem^i:3h:nconsume^i:h:playsfx^f:h:stat_targetstrength^s:'
'T{h:condtype:2h:val:t{%_chainbits%}:bits:}:chain^h:T{%_chaintuple%}:elsechain:T{%_chaintuple%}:insteadchain:'
'h:learnsfx^f:T{h:newenemy:h:hpchange:h:statchange:}:transmogrify:64T{h:cond:f:threshold:}:failelementalattack:') # XXX import from lumpdefs.yaml
defpal = 'h:defpal:'
defpass = '160H:passability:h:magicnumber:'
fixbits = '3B' # 23 bits used (see http://rpg.hamsterrepublic.com/ohrrpgce/FIXBITS.BIN)
lookup1 = 'h:id:38s:scriptname:'
menus = '22s:name:h:style:h:default_textcolor:h:maxrows:2B:bitsets:T{%coord%}:offset:T{%coord%}:anchor:h:textalign:T{%range%}:width:'
'h:borderthickness:h:onclose_trigger:h:quit_menu:'
#menuitem = 'h:owner:40s:caption:h:sortorder:h:type:h:subtype:2h:tagconditional:h:settag:h:toggletag:t{?:hidewhendisabled:?:closemenuswhenselected:?:dontrunonclosescr:<u12}:bitsets:3h:extra:'
# menuitem = 'h:owner:40s:caption:h:sortorder:h:type:h:subtype:2h:tagconditional:h:settag:h:toggletag:2B:bitsets:3h:extra:'
palettes = '(256,3)B'
plotscr = 'h:id:38s:name:'
songdata = '32s:name:'
sfxdata = '32s:name:h:streaming:'
uicolors = 'h:background^m:h:menuitem^m:h:disabledmenuitem^m:2h:selection^m:2h:selecteddisabled^m:h:highlight^m:h:equiphighlight:'
'h:timebar^b:h:timebarfull^b:h:healthbar^b:h:healthbarfull^b:h:text^t:h:outline^t:h:description:h:gold:15h:textbox^t:15h:textboxframe^t'

font = DType ('(256,)8B:characters:', characters = packedimage (bpp = 1, packing = 'y>'))
item = DType ('V18:name:V72:info:h:value:h:battleattack:h:weaponattack:h:equippable_as:h:teach_spell:h:oob_use:'
              'h:weapon_picture:h:weapon_palette:T{%stats%}:bonuses:8B:equippable_by:3B:bitsets:'
              'h:consumability:V8:tagsets:T{h:x:h:y}:frame2_handle:T{h:x:h:y}:frame1_handle:64f:elem_resistance:'
               name = pascalstring ('hh'), info = pascalstring ('hh'),
               equippable_as = enum ('Never_equipped Weapon Armor_1 Armor_2 Armor_3 Armor_4'),
               teach_spell = offsetby(+1) + record_limited('attack'),
               oob_use = splitenum('textbox_number','nothing', 'attack_number') + record_limited('textbox','attack'),
               weapon_palette = default(-1),
               equippable_by = bitsets(['by_%02d' % v for i in range(41)]),
               tagsets = DType ('h:own_item:h:item_in_inventory:h:is_equipped:h:equipped_by_active_hero:' __all__ = tagset()
               
               
               
               
               


# XXX belongs in DataDescription


#uicolors_dd = D(check = {ALL : '0 <= v <= 255'})

#'T{h:headersize:h:recordsize:}:header:'

def test():
    for k,v in globals().items():
        if k.startswith ('__'):
            continue
        if type(v) == str:
            ok = False
            try:
                dt = dtype (v, namespace = globals())
                ok = True
            except ValueError as e:
                raise
                #print (e)
            ok = 'OK' if ok else 'FAIL\n'
            print ('%-10s %-5s' % (k,ok), end= '')
            if ok=='OK':
                print ('\t%-50s %3d bytes' % (dt, dt.itemsize))

test()

def test_read(wd):
    pass
