# ****************************
# Ohrrpgce Data I/O system
# ****************************
#
# :Version: 1
# :Author: David Gowers <00ai99@gmail.com>
#
#
# .. contents::
#
# Preface
# +++++++++++++++++++++
#
# Changelog
# ===============
# see :doc: git-changelog
#
# Introduction
# =============
#
# OHRRPGCE data is currently pretty inaccessible, despite
# the advances of rpgdirs, most things are opaque binary blobs.
# There are several related issues to address:
#
# * transferring data between OHRRPGCE rpg files
# * inspection and modification of data (eg. easy construction
#   of helper tools)
# * wider-world portability (SQL querying? grepping?)
#
# It was initially (ill)-conceived as a simple hack as I was polishing
# my understanding of numpy dtypes -- 'well, we can dump this to YAML,
# it's not too hard; and we can get all sorts of nice side effects from that,'
#
# This looked nice, but data nesting required a more methodical approach
# than I was willing to apply. Development crawled along for a while --
# one of the things I got right was that NumPy dtyping would allow
# simple maintenance and even
#
# .. todo:: simple multi-version support
#
# So even as I was baffled over it's ultimate fate, I felt secure in
# adding support for more dtypes.
#
# This distraction arose from a shallow understanding of YAML -- and my
# everpresent frantic approach.
#
# I began to understand this would not be so simple, and refactored the
# code from a mess of bits embedded in a doctest, into this file --
# ``ohrrpgce.py``
#
# More recently, I found pylit_ and, understanding that literate
# programming will help me to moderate my franticnesses and be more
# rational, I embarked on converting ``ohrrpgce.py`` to pylit_ format
# -- which is a mix of two of my joys in programming, ReStructuredText
# and Python :)
#
# I'll now attempt to clearly conceptualize this system.
#
# NOHRIO
# ========
#
# NOHRIO is the name of this module.
# It's N___ OHR I/O (nice? neat? nifty? nictating?)
# Pronunciation: Noh Rio
#
# Code
# +++++++++
#
# Setup
# ===============
#
# We use numpy to specify, load, and save all of OHRRPGCE's
# formats. Its dtype system is extremely powerful, and the
# nesting is key to 'nice' access and slicing-up of the data.
#

import numpy as np
import os
from ohrstring import *

# Helper data
# ----------------
#
# This is kind of a mess of macro-ish things that
# simplify construction of dtypes :|
#


BLOAD_HEADER = ('bload_header', (np.uint8, 7))
BLOAD_SIZE = 7

# INT is the most common datatype in OHRRPGCE.
# ``numpy.dtype ('h')`` gives you an int16 dtype
# however, ``numpy.dtype ('INT') gives you a uint16 dtype :(
#
# think this out better.
#

INT = np.int16
def XXXfieldlist_to_dtype (fields):
    fields = fields.split()
    return [(field,INT) for field in fields]

def mmap (fname, dtype, offset = 0, shape = None, order = 'C'):
    return np.memmap (fname, dtype = dtype, mode = 'r',
                      offset = offset, shape = shape, order = order)

def make (*allnames, **corrections):
    names = []
    formats = []
    for somenames in allnames:
        somenames = somenames.split()
        names.extend (somenames)
        formats.extend ([INT] * len (somenames))
    for name, format in corrections.items():
        formats[names.index(name)] = format
    return np.dtype ({'names': names, 'formats': formats})


# YAML: identify the object type
# vamji-translate special lo vamji pe special ckiku
#
# invalid characters like binary 0 should be translated to \\00

# make = from_fieldnames

def fvstr (maxlen):
    return np.dtype([('length', INT), ('value', (np.character, maxlen))])

# some formats have all the x, then all the y, ..
#
# .. warning::
#
#     This function is obsolete!
#     Using order = 'F' parameter to mmap
#     allows planar on-disk format with completely
#     reasonable indexing.
#     Use the 'linear' variants of the dtype with order = 'F'.

def planar_dtype (fieldnames, num, dtype, bload = False):
    dt = []
    if bload:
        dt.append (BLOAD_HEADER)
    for field in fieldnames.split():
        dt.append ((field, (dtype, num)))
    return np.dtype (dt)




# Certain sorts of simple analysis prefer flattened dtypes or
# simplified dtypes.
#
# Simplified dtypes
# =================
#
# TeeEmCee raised the issue of field nesting being unnecessarily
# convoluted.
#
# This is my attempt to address the issue;

def simplify_dtype (dtype):
    """Make things easier for TMC.

    Really, reduces the amount of dereferencing
    needed to access sufficiently simple dtypes.

    drawing an analogy to paths, we simplify the following:

    name/fields -> fields where name is the only top level field

    name/name/../field -> (dtype of field) where field is the only bottom level field.

    """
    import numpy as np
    if type (dtype) != np.dtype:
        dtype = np.dtype (dtype)
    dtype = dtype.descr
    newdtype = []
    if len (dtype) == 1 and type (dtype[0][1]) == list:
        newdtype.append (simplify_dtype (np.dtype(dtype[0][1])))
    else:
        return dtype
    while type (newdtype[0]) == list:
        newdtype = newdtype[0]
    if len (newdtype) == 1: # single field
        newdtype = newdtype[0][1:]
    return np.dtype (newdtype)

def flatten_dtype (dtype, prefix = '', suffix = '', flatten_arrays = False):
    """Eliminate dtype nesting.

    Returns
    --------
    flattened : dtype
                With the same fields (essentially)
                in the same order,
                with no nesting

    Notes
    ------

    foo/bar field becomes foobar field.
    1d arrays foo/bar+foo/bif become
    foobar0, foobif0, foobar1, foobif1, ..

    optionally, 1d subarrays are also flattened.
    (>=2d subarrays are currently unhandled.)
    """
    import numpy as np
    if type (dtype) != np.dtype:
        dtype = np.dtype (dtype)
    dtype = dtype.descr
    newdtype = []
    for item in dtype:
        multiple = len (item) == 3
        if type (item[1]) == list:
            if multiple:
                for i in range (item[2]):
                    flattened = flatten_dtype (np.dtype (item[1]),
                                               prefix + item[0] + suffix,
                                               suffix + str (i),
                                               flatten_arrays)
                    newdtype.extend (flattened.descr)
            else:
                flattened = flatten_dtype (np.dtype (item[1]),
                                           prefix + item[0] + suffix,
                                           suffix,
                                           flatten_arrays)
                newdtype.extend (flattened.descr)
        else:
            if multiple and flatten_arrays:
                for i in range (item[2]):
                    newdtype.append (('%s%s%s%d' % (prefix,
                                                    item[0], suffix, i),
                                     item[1]))
            else:
                newdtype.append ((prefix + item[0] + suffix,) + item[1:])
    return np.dtype (newdtype)

def fix_stringjunk (arr, fields = None, doubled = False):
    fields = fields or arr.dtype.names
    for name in fields:
        for item in arr[name]:
            if doubled:
                tmp = str(item['value'])[:item['length'] * 2]
                tmp = list(tmp)
                tmp[1::2] = ['.'] * (len (tmp) / 2)
                tmp = "".join (tmp)
            else:
                tmp = str(item['value'])[:item['length']]
            item['value'] = tmp

def pad (filename, granularity, groupsize = 1, headersize = 0):
    filesize = os.path.getsize (filename)
    nrecordsets = (filesize - headersize) / float (granularity * groupsize)
    padding = ''
    fullrecordsize = (int (nrecordsets) * (granularity * groupsize)) + headersize
    if fullrecordsize < filesize:
        nrecordsets = round (nrecordsets + 0.499999999999)
        padding = '\x00' * (int (nrecordsets) *
                            (granularity * groupsize) - filesize)
    if padding == '':
        return int (nrecordsets) / groupsize
    f = open (filename, 'ab')
    f.seek (1, 2)
    f.write (padding)
    f.close ()
    filesize = os.path.getsize (filename)
    nrecords = (filesize - headersize) / granularity
    return nrecords

# Wrappers
# ===========
#
# XXX these virtualize things in a way contradictory to the
# ohr / bin / text trichotomy:
#
# nohrio conceptualizes of three classes of format for OHR data to be
# stored in.
#
# 1. plain. textual or trivially converted to text. eg YAML, internal
#    dictionary format.
#    This data must be self-encapsulated
#    (ie. it can refer to other objects,
#    however understanding its meaning is not dependent on
#    outside factors.)
#
#    Note that only a certain subset of XML can qualify here
#    -- that which uses no attributes.
#
#    It must behave like a dict; especially, it must accept and store arbitrary
#    key values, and it must represent itself as MyClass(dict-style init params).
#    it should serialize as YAML like:
#
#    .. code-block:: yaml
#
#       - myclass : #(lower cased)
#           - key : value
#           - key : value
#
#
# 2. OHR native. weird hacks, possibly with weirdly hacky headers.
#
# 3. Binary (sane). In a self-describing format such as SQLite, HDF5,
#    or numpy storage (in memory or on disk).
#    Known junk bytes are expected to be discarded,
#    bytes of unknown meaning must be preserved verbatim.
#
# In the case of #2, aggregation schemes are strictly limited.
# In the case of #1 and #3, aggregation schemes are flexible.
# #3 will generally add description of what items are aggregated
# as a separate object per array. #1 may embed this data in the object
# itself.
#
# both #1 and #3 can hold information beyond the 'base set' --
# eg YAML supports arbitrary keys, and HDF5 supports complex array
# attributes. #2 explicitly discards this information.
# Storing it inside the RPG file is undesirable because it cannot be
# guaranteed to be in sync (and after a little editing, may almost be
# guaranteed not to be in sync.)
#
# *PS*. we can use SHA-1 hashing to determine whether metadata is up to date
# (ie. is metadata about exactly the same object.)
#
#
# To simplify this scheme, I also designate the following data transformation flow:
#
# OHR <> binary <> plain
#
# That is, conversion is done between OHR and binary;
# and binary and plain; but not OHR and plain.
#
# Q: Why can't we just have #1 and #2 without #3?
#    Balance between inspectability and ease of modification.
#    Want to multiply all enemies HP by 1.5,
#    and have enemy data in a NumPy array or memmap?
#    A fast ``arr['stats']['hp'] *= 1.5`` vs a slow
#    ``for enemy in enemies: enemy['hp'] *= 1.5.``
#
#    However, on reflection, SQLite satisfies the inspectability AND
#    speed criteria. So if this is satisfactory, you could exclude the
#    text format instead.

# The following two classes both accept either a filename or a file handle
# (which must support the ``seek()``, ``write()`` and ``read()`` methods')
#
# when accessing RPG files 'inline' (without unlumping them first)
# you should specify offset like this::
#
#     offset = rpgfile.tell() # this should point at the start of the lump data
#     fixbits = fixBits (rpgfile, offset)

def filename_or_handle (f, mode):
    if type (f) in (str, unicode):
        return open (f, mode)
    return f

class fixBits (object):
    fields = ['attackitems', 'weappoints', 'stuncancel',
              'defaultdissolve', 'defaultdissolveenemy',
              'pushnpcbug_compat', 'default_maxitem', 'blankdoorlinks',
              'shopsounds', 'extended_npcs', 'heroportrait',
              'textbox_portrait', 'npclocation_format', 'initdamagedisplay']
    def __init__ (self, file, offset = 0, **kwargs):
        self.file = filename_or_handle (file, 'rb+')
        self.origin = offset
        self.file.seek (offset)
        for k, v in kwargs.items():
            setattr (self, k, v)
    def save (self, f):
        self.file.seek (self.origin)
        f.write (self.file.read())
    def tostring (self):
        self.file.seek (self.origin)
        return self.file.read()
    def __getitem__ (self, k):
        if type (k) == slice:
            return [self.__getattr__ (v) for v in self.fields[k]]
        return self.__getattr__ (self.fields[k])
    def __setitem__ (self, k, v):
        if type (k) == slice:
            for key, value in zip (self.fields[k], v):
                self.__setattr__ (key, value)
        else:
            self.__setattr__ (self.fields[k], v)
    def __getattr__ (self, k):
        try:
            k = object.__getattribute__ (self, 'fields').index (k)
        except ValueError:
            return object.__getattribute__ (self, k)
        self.file.seek (self.origin + (k / 8))
        result = ord (self.file.read(1)) & (1 << k % 8)
        if result > 0:
           return 1
        else:
           return 0
    def __setattr__ (self, k, v):
        try:
            k = object.__getattribute__ (self, 'fields').index (k)
        except ValueError:
            object.__setattr__ (self, k, v)
            return
        self.file.seek (self.origin + (k / 8))
        value = ord (self.file.read (1))
        if value & (1 << k % 8):
            value ^= (1 << k % 8)
        if v:
            value |= (1 << k % 8)
        self.file.seek (self.origin + (k / 8))
        self.file.write (chr (value))
    def __repr__ (self):
        kwargs = ", ".join (['%s = %d' % (name, v) for name, v in zip (self.fields, self)])
        return "%s (%r, %s)" % (self.__class__.__name__, self.file.name, kwargs)
    def __iter__ (self):
        return [getattr (self, k) for k in self.fields].__iter__()
    def __gc__ (self):
        self.file.close()

#
# archinym.lmp
# ---------------
#
# Read-write if accessing an unlumped file,
# read-only if accessing a section of an rpg file 'inline'.
# This is because the size of the lump may change during writing.
#

class archiNym (object):
    def __init__ (self, file, offset = 0, **args):
        mode = 'rb+'
        if offset > 0:
            mode = 'rb'
        self.file = filename_or_handle (file, mode)
        self.origin = offset
        if offset:
            self.file.seek (offset)
        for k, v  in enumerate (args):
            self[k] = v
    def __getitem__ (self, k):
        assert (-1 < k < 2)
        self.file.seek (self.origin)
        for i in range (k):
            self.file.readline()
        return self.file.readline().rstrip()
    def __setitem__ (self, k, v):
        assert (-1 < k < 2)
        everything = [self[0], self[1]]
        self.file.seek (self)
        everything [k] = v
        for value in everything:
            self.file.write (value + '\x0d\x0a')
    def __repr__ (self):
        return '%s (%r, %r, %r)' % (self.__class__.__name__,
                                    self.file.name,
                                    self[0], self[1])
    def _getprefix (self):
        return self[0]
    def _setprefix (self, v):
        self[0] = v
    def _getversion (self):
        return self[1]
    def _setversion (self, v):
        self[1] = v
    prefix = property (_getprefix, _setprefix)
    version = property (_getversion, _setversion)


def seq_to_str (src):
    """convert a length,..,[charvalue,charvalue,..] sequence to a normal string."""
    return "".join([chr(v) for v in src[-1][:src[0]]])

def adjust_for_binsize (dtype, binsize):
    dtsize = np.dtype (dtype).itemsize
    while dtsize > binsize:
        dtype['names'].pop()
        dtype['formats'].pop()
        dtsize = np.dtype (dtype).itemsize
    if dtsize != binsize:
        raise ValueError ('dtype is misaligned with binsize!')

def vstr (len):
    "dtype of an OHRRPGCE string (BYTE length, BYTE-based characters) totaling ``len`` bytes"
    return np.dtype ([('length', np.uint8),('value', (np.character, len - 1))])

def vstr2 (len):
    "dtype of an OHRRPGCE string (SHORT length, SHORT-based characters) totaling ``len`` bytes"
    return np.dtype ([('length', np.uint16),('data', (np.character, (len - 1) * 2))])

_statlist = 'hp mp str acc def dog mag wil spd ctr foc xhits'.split()
STATS_DTYPE = [(name, INT) for name in _statlist]
STATS0_99_DTYPE = [(name, (INT, 2)) for name in _statlist]
xycoord_dtype = [('x', INT), ('y',INT)]
_browse_base_dtype = [('length', INT), ('value', (np.character, 38))]
_rgb16_dtype = np.dtype ([('r', np.uint16,), ('g', np.uint16), ('b', np.uint16)])
_saychoice_dtype = [('name' , [('length', 'B'), ('value', 'S14')]), ('tag', INT)]
_saytagpair_dtype = [('tagcheck', INT), ('param', INT)]
_say_conditionals_dtype = [('jumptoinstead', _saytagpair_dtype), ('settag', [('tagcheck', INT), ('tagset1', INT), ('tagset2', INT)])]
_say_conditionals_dtype += [('fight', _saytagpair_dtype), ('shop', _saytagpair_dtype)]
_say_conditionals_dtype += [('hero', _saytagpair_dtype), ('jumptoafter', _saytagpair_dtype)]
_say_conditionals_dtype += [('money', _saytagpair_dtype), ('usedoor', _saytagpair_dtype)]
_say_conditionals_dtype += [('items', [('tagcheck', INT), ('item', INT), ('heroswap', INT), ('herolock', INT)])]

# Shapes of pt? graphics data
# ===========================
#
# frames, w, h order (ie on-disk format)

ptshapes = ((8, 32, 40), (1, 34, 34), (1, 50, 50), (1, 80, 80), (8, 20, 20),
            (2, 24, 24), (3, 50, 50), (16, 16, 16), (1, 50, 50))

_spell_list = ([('attack', INT), ('level', INT)], (4, 24))


# Data type definitions
# =====================
#
# I want to merge 'dtypes_' and  'textserialize_dtype_tweaks_'
#
# .. _dtypes:
#
# Data type groupings
# --------------------
#
# Graphics
# ~~~~~~~~~
#
# * palettes_
# * sprites_
# * background_
#
# Battle
# ~~~~~~~
#
# * attacks_
# * enemies_
# * heroes_
# * battles_

_attack_chain_info = make ('attack cond_type rate cond_value cond_value2 bitsets',
                           bitsets = ('B', 2))
#
# General
# ~~~~~~~~
#
# * items_
# * shops_
# * maps_
#
# Metadata
# ~~~~~~~~~
#
# * defaults_
# * formatinfo_
# * trimmings_



dtypes = {
# Attack data
# ============
#
# a concatenation of DT6 and ATTACK.BIN.
#
# To avoid hacks,
# we do not negotiate with attack.bin or dt6, only the sane spliced data.
#
# Backwards compatibility may require you to chop fields off the end here
# until dtype.itemsize matches the size specified in BINSIZE.BIN.
#
    'attack.full' : make ('picture palette animpattern targetclass targetsetting',
                          'damage_eq aim_math baseatk_stat cost xdamage chainto','chain_percent',
                          'attacker_anim attack_anim attack_delay nhits target_stat',
                          'preftarget bitsets1 name captiontime caption basedef_stat',
                          'settag tagcond tagcheck settag2 tagcond2 tagcheck2 bitsets2',
                          'description consumeitem nitems_consumed soundeffect',
                          'stat_preftarget chaincond_type chaincond_value',
                          'chaincond_value2 chain_bitsets else_chain instead_chain learn_sound',
                          bitsets1 = ('B', 64 / 8), bitsets2 = ('B', 128 / 8),
                          cost = [('hp', INT), ('mp', INT), ('money', INT)],
                          name = [('length', INT), ('unused', INT), ('data', (np.character, 10*2))],
                          caption = fvstr (40),
                          consumeitem = (INT, 3),
                          nitems_consumed = (INT, 3),
                          description = fvstr (38),
                          chain_bitsets = ('B', 2),
                          else_chain = _attack_chain_info,
                          instead_chain = _attack_chain_info),

    'binsize.bin' : make ('attack stf songdata sfxdata map',
                          'menu menuitem uicolor say'),
    'browse.txt' : np.dtype ([('longname', _browse_base_dtype),
                              ('about', _browse_base_dtype)]),
    'defpass.bin' : np.dtype ([('passability', (INT, 160)), ('magic', INT)]),
    'defpal%d.bin' : np.dtype ([('palette', INT)]),
    'd' : planar_dtype ('srcdoor destdoor destmap condtag1 condtag2', 100, INT),
    'd.linear' : make ('srcdoor destdoor destmap condtag1 condtag2'),
    'dox' : planar_dtype ('x y bitsets',100, INT),
    'dt0' : make ('name battlepic battlepal walkpic walkpal defaultlevel defaultweapon',
                  'stats spells portraitpic bitsets spelllist_name portraitpal spelllist_type',
                  'have_tag alive_tag leader_tag active_tag',
                  'maxnamelength handcoord',
                  " ".join (["%sframe" % name for name in 'stand step attacka attackb cast hurt weak dead \
                  dead2 targetting victorya victoryb'.split()]),
                  'unused',
                  name = vstr2 (17),
                  stats = STATS0_99_DTYPE,
                  spells = _spell_list,
                  bitsets = (np.uint8, 48 / 8),
                  spelllist_name = ([('length', INT), ('data', (np.character, 10*2))], 4),
                  spelllist_type = (INT, 4),
                  handcoord = (xycoord_dtype, 2),
                  unused = (INT, 5)),
    'dt1' : make ('name thievability stealable_item stealchance',
                  'raresteal_item raresteal_chance dissolve dissolvespeed',
                  'deathsound unused picture palette picsize rewards stats',
                  'bitsets spawning attacks unused2',
                  name = vstr2 (17),
                  rewards = make ('gold exp item itemchance rareitem rareitemchance'),
                  bitsets = ('B', 10),
                  spawning = make ('death non_e_death alone non_e_hit',
                                   'elemhit n_tospawn',
                                   elemhit = (INT, 8)),
                  attacks = [('regular', (INT, 5)), ('desperation', (INT, 5)),
                             ('alone', (INT, 5)), ('counter', (INT, 8))],
                  stats = STATS_DTYPE,
                  unused = (INT, 28),
                  unused2 = (INT, 45)),
    'efs' : np.dtype ([('frequency', INT),('formations',(INT, 20)),
                       ('wasted', (INT, 4))]),
    'for' : make ('enemies background music backgroundframes backgroundspeed unused',
                  enemies = (make ('type x y unused'), 8), unused = (INT, 4)),
    'fnt' : np.dtype ([('characters', [('bitmaps', np.uint8, (256, 8))])]),
    'gen' : make ('maxmap title titlemusic victorymusic battlemusic',
                  'passcodeversion passcoderotator newpasscode newpasscode_unused',
                  'oldpasscode',
                  " ".join(['max%spic' % name for name in 'hero','enemy1','enemy2','enemy3','npc','weapon','attack']),
                  " ".join(['max%s' % name for name in 'tileset','attack','hero', 'enemy', 'formation','palette','textbox','plotscript']),
                  'newgamescript gameoverscript max_regularscript suspendbits cameramode',
                  'camera_args scriptbackdrop time maxvehicle maxtagname',
                  'loadgamescript textbox_backdrop enemydissolve enablejoy',
                  'poison stun damagecap mute statcap maxsfx masterpal',
                  'maxmasterpal maxmenu maxmenuitem maxitem max_boxborder',
                  'maxportrait maxinventory reserved',
                  'oldpassword2_offset oldpassword2_length version startmoney',
                  'maxshop oldpassword1_offset oldpassword1_length maxbackdrop',
                  'bitsets startx starty startmap onetimenpc_indexer',
                  'onetimenpc_bits',
                  'def_deathsfx maxsong acceptsfx cancelsfx choosesfx textboxletter',
                  'morebitsets itemlearnsfx cantlearnsfx buysfx hiresfx sellsfx',
                  'cantbuysfx cantsellsfx damagedisplayticks damagedisplayrise',
                  'wastedspace oldsctable_head oldsctable unused',
                  newpasscode = (np.uint8, 17), newpasscode_unused = np.uint8,
                  oldpasscode = (INT, 10), suspendbits = np.uint16,
                  camera_args = (INT, 4), time = (INT, 4),
                  statcap = (INT, 12), reserved = (INT, 7),
                  bitsets = np.uint16, onetimenpc_bits = (np.uint8, 130),
                  morebitsets = (np.uint8,4), wastedspace = (INT,11),
                  oldsctable_head = np.uint16, oldsctable = (np.uint16, 160),
                  unused = (np.uint16, 140)),
    'itm' : make ('name info value attack weaponattack equippable teach oobuse weaponpic weaponpal',
                  'bonuses equippableby bitsets consumability own_tag in_inventory_tag equipped_tag',
                  'equippedby_active_tag frame2handle frame1handle unused',
                  name = vstr2 (9), info = vstr2(36),
                  bonuses = STATS_DTYPE,
                  equippableby = ('B', 8),
                  bitsets = ('B', 6),
                  frame2handle = xycoord_dtype,
                  frame1handle = xycoord_dtype,
                  unused = (INT, 19)),
    'l' : planar_dtype ('x y id dir walkframe',300,INT, bload = True),
    'l.linear' : make ('x y id dir walkframe'),
    'map' : make ('tileset music minimap_available save_anywhere display_name_time',
                  'edge_mode edge_tile autorun_trigger autorun_arg harmtile_damage',
                  'harmtile_flash foot_offset afterbattle_trigger',
                  'insteadofbattle_trigger each_step_trigger keypress_trigger draw_herosfirst',
                  'npcanddoor_loading tileandwall_loading bitsets savoffset layer_tilesets',
                  'n_npc_instances', savoffset = xycoord_dtype, bitsets = ('B', 2),
                  layer_tilesets = (INT, 3)),

# .. _mxs:
#
# 320x200 Backdrops
# -------------------
#
# til_ is also the same format

    'mxs' : np.dtype ([('planes', (np.uint8, (4, 16000)))]),

# some variant dtypes.
#
# ``mxs.linear`` is the sensible format that I wish OHR used.
# it is good for external serializations. Ignore it otherwise.
#
# ``mxs.planar`` is somewhat in-between -- it presents a planar
# view on 80x200 bitmaps. This is fully accurate to the OHRRPGCE file format;
# it may replace ``mxs`` dtype in the future.
#
# to translate between them:
#
# ``for i in range (4): linear[:,i::4] = planar[i]``
#

    'mxs.planar' : np.dtype ([('pixels', (np.uint8, (4, 200, 80)))]),
    'mxs.linear' : np.dtype ([('pixels', (np.uint8, (200, 320)))]),

    'menuitem.bin' : make ('membership caption sort_order type subtype',
                           'tagcond1 tagcond2 settag toggletag bitsets extra',
                           extra = (INT,3), bitsets = ('B',2), caption = fvstr (38)),
    'menus.bin' : make ('name boxstyle default_textcolor maxrows bitsets offset anchor',
                        'textalign minwidth maxwidth border_thickness',
                        name = fvstr (20), bitsets = ('B', 2),
                        offset = xycoord_dtype, anchor = xycoord_dtype),
    'mn' : np.dtype ([('length', 'B'), ('value', 'S79')]),
    'n' : make ('picture palette movetype speed showtext',
                'activate_action giveitem pushability activation',
                'appear_if_tag1 appear_if_tag2 usability trigger',
                'script_arg vehicle'),

# .. _pal:
#
# 16 color palettes
# -----------------
#
# does this need to be un-nested?

    'pal' : np.dtype ([('indices', 'B', 16)]),

# .. _palettes_bin:
#
# New master palettes
# -------------------
#
# :since: ubersetzung
# :obsoletes: mas_

    'palettes.bin' : np.dtype ([('color', ([('r', np.uint8),
                                            ('g', np.uint8),
                                            ('b', np.uint8)], 256))]),
    'plotscr.lst' : np.dtype ([('id', INT), ('name', fvstr(36))]),

# .. _say:
#
# Text boxes
# -----------

    'say' : make ('text reserved1 conditional reserved2 choicebitsets choice1 wasted choice2',
                  'menuconditional verticalpos shrink textcolor bordercolor backdrop music menu',
                  'portraittype portraitpic portraitpal portraitx portraity',
                  text = ('S38', 8), reserved1 = 'B', conditional = _say_conditionals_dtype,
                  reserved2 = 'B', choicebitsets = 'B', choice1 = _saychoice_dtype,
                  wasted = 'B', choice2 = _saychoice_dtype),
    'sfxdata.bin' : np.dtype ([('name', fvstr (30)), ('streaming', INT)]),
    'sho' : np.dtype ([('name', vstr2 (16)), ('nitems', INT), ('bitsets', ('B',2)),
                  ('inncost', INT), ('innscript', INT)]),
    'songdata.bin' : np.dtype ([('name', fvstr (30))]),
    '_stf_item' : make ('name type number in_stock buyreq_tag sellreq_tag buyset_tag sellset_tag',
                  'buyprice req_tradeitem1 selltype sellprice tradefor tradefor_amount',
                  'req_tradeitem1_n req_tradeitem2 req_tradeitem2_n req_tradeitem3',
                  'req_tradeitem3_n req_tradeitem4 req_tradeitem4_n',
                  'buyprice_defaulter sellprice_defaulter unused',
                  name = vstr2 (17), unused = (INT, 3)),

# .. _tap:
#
# Tile animation patterns
# ------------------------

    'tap' : np.dtype ([('starttile', INT), ('disable_if_tag', INT),
                       ('actiontype', (INT,9)), ('actionparam', (INT,9))]),

# .. _tmn:
#
# Tag names
# ---------------
#

    'tmn' : vstr2 (21),

# .. _uicolors_bin:
#
# UI colors
# ----------

    'uicolors.bin' : make ('background menuitem disableditem selecteditem selecteddisabled',
                           'highlight timebar timebarfull healthbar healthbarflash text',
                           'outline description gold shadow textbox textboxframe',
                           selecteditem = (INT, 2), selecteddisabled = (INT, 2),
                           highlight = (INT, 2),
                           textbox = ([('bg', INT), ('border', INT)], 15),
                           textboxframe = (INT, 15)),

# .. _veh:
#
# Vehicles
# ---------

    'veh' : make ('name speed bitsets randbattles usebutton menubutton ridingtag onmount',
                  'ondismount overridewalls blockedby mountfrom dismount_to elevation reserved',
                  name = vstr (16), bitsets = (np.uint8, 4), reserved = (INT, 18)),
    }


# Deprecated dtypes
# ==================

deprecated_dtypes = {

# Second part of attack data
# ---------------------------
#
# .. note::
#
#     memmapping with this dtype causes a crash!
#     load the data into a normal array with this dtype,
#     or use the full spliced dtype 'attack.full'

    'attack.bin' : make ('captionpt2 basedef_stat',
                         'settag tagcond tagcheck settag2 tagcond2 tagcheck2 bitsets3',
                         'description consumeitem nitems_consumed soundeffect',
                         'stat_preftarget',
                         bitsets3 = ('B', 128 / 8),
                         captionpt2 = 'S36',
                         description = fvstr (38),
                         consumeitem = (INT, 3),
                         nitems_consumed = (INT, 3)),

# First part of attack data
# ---------------------------

    'dt6' : make ('picture palette animpattern targetclass targetsetting',
                  'damage_eq aim_math baseatk_stat cost xdamage chainto chain_percent',
                  'attacker_anim attack_anim attack_delay nhits target_stat',
                  'preftarget bitsets1 name captiontime captionpt1',
                  bitsets1 = ('B', 64 / 8),
                  cost = [('hp', INT), ('mp', INT), ('money', INT)],
                  name = [('length', INT), ('unused', INT), ('value', 'S20')],
                  captionpt1 = fvstr (4)),

# .. _mas:
#
# Old master palettes
# -------------------
#
# :obsolete: Yes

    'mas' : np.dtype ([('color', _rgb16_dtype, 256)]),

}

def names (nameliststring, length = -1, **aliases):
    tmp = nameliststring.split(';')
    if length > 0 and len(tmp) < length:
        tmp.extend(['UNDEFINED%d' % v for v in range(len(tmp), length)])
    return tmp

# Ignore this for now.
#
# .. _textserialize_dtype_tweaks:

textserialize_dtype_tweaks = {
    # per http://gilgamesh.hamsterrepublic.com/wiki/ohrrpgce/index.php/[NAME]
    # list of formats to check:
    #
    # _ATTACK _stf_item ATTACK.BIN -binsize.bin -browse.txt d -defpal%d.bin
    # defpass.bin dox dt0 dt1 dt6 efs fnt for gen itm l map -mas
    # menuitem.bin menus.bin mn mxs n pal palettes.bin -plotscr.lst
    # pt0 pt1 pt2 pt3 pt4 pt5 pt6 pt7 pt8 say sfxdata.bin SHO
    # songdata.bin stf stt tap til tmn uicolors.bin veh
    '_attack' : { ('bitsets','bitsets2') : names('abitset;anotherbitset')},
    'attack.bin' : { ('bitsets3',) : names('')},
    'menus.bin' : {'bitsets' : names ('transparent box;'
                                      'never show scrollbar;'
                                      'allow gameplay while menu is active;'
                                      'suspend player even if gameplay allowed;'
                                      'no box;'
                                      'cancel button doesnt close menu;'
                                      'no player control of menu;'
                                      'prevent main menu from opening;'
                                      'advance text box when menu closes',16)},
    'l' : {'dir' : names('up;right;down;left', u='up', r='right',
                                               l='left', d='down')},
    # future: represent pushability as a bitfield with ULDR 'bit's
    'n' : {'pushability' : names ('off;full;horizontal;vertical;'
                                  'up only;right only;down only;left only',
                                  )},
    'sho' : { 'bitsets' : names ('buy;sell;hire;inn;equip;save;map;team')},
    'veh' : { 'bitsets' : names ('pass thru walls;pass thru npcs;'
                                 'enable npc activation;enable door use;'
                                 'do not hide leader;do not hide party;'
                                 'dismount one space ahead;'
                                 'pass walls while dismounting;'
                                 'disable flying shadow', 32)}
    }

del _browse_base_dtype

# .. _til:
#
# Tilesets
# ---------
#
# .. seealso:: mxs_



dtypes['til'] = dtypes['mxs']
dtypes['til.linear'] = dtypes['mxs.linear']
dtypes['til.planar'] = dtypes['mxs.planar']


# gfx4bpp
# =======
#
# Description of formatting parameters for an 16color image array
# FRAMExHxW (where frame may be 1 ie an implicitly omitted dimension)
#
# Serializes to YAML as:
#
# .. code-block:: yaml
#
#    imagearray :
#      - bpp : 4
#      - width : W
#      - height : INT
#      - frames : F
#      - pixels :|
#                 001100
#                 011210
#                 312322
#                 211213
#                 021120
#                 001100
#      - pixels :|
#                 001100
#                 031210
#                 212321
#                 211212
#                 011130
#                 001200
#      - and # so on.. (1 pixels record for each frame)
#
# Pixels are shown in hex -- ie values are translated to 0123456789ABCDEF

class Gfx4bpp (tuple):
    pass


# .. _ptx:
#
# 16-color graphics
# -----------------

for i, data in enumerate (ptshapes):
    w, h, frames = data
    dtypes['pt%d' % i] = [('pixels', (np.uint8, (w/2) * h * frames))]
    dtypes['alt-pt%d' % i] = [('images', np.uint8, (frames, h, w / 2))]
    textserialize_dtype_tweaks['pt%d' % i] = {'pixels' : Gfx4bpp ((w, h, frames))}

del w, h, frames, i, data

STT_LENGTHS = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1,
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2,
               2, 1, 2, 1, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2,
               2, 2, 1, 3, 3, 3, 2, 2, 1, 1, 1, 1, 1, 1, 3,
               2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1,
               1, 1]

STT_NAMES = ['Health_Points', 'Spell_Points', 'Attack_Power', 'Accuracy',
             'Extra_Hits', 'Blocking_Power', 'Dodge_Rate', 'Counter_Rate',
             'Speed', 'Enemy_Type_1', 'Enemy_Type_2', 'Enemy_Type_3',
             'Enemy_Type_4', 'Enemy_Type_5', 'Enemy_Type_6', 'Enemy_Type_7',
             'Enemy_Type_8', 'Elemental_1', 'Elemental_2', 'Elemental_3',
             'Elemental_4', 'Elemental_5', 'Elemental_6', 'Elemental_7',
             'Elemental_8', 'Armor_1', 'Armor_2', 'Armor_3', 'Armor_4',
             'Spell_Skill', 'Spell_Block', 'Spell_cost__', 'Money', 'Experience',
             'Item', 'DONE', 'AUTOSORT', 'TRASH', 'Weapon', '_REMOVE_',
             '_EXIT_', 'Discard', 'Cannot', 'Level', 'Yes', 'No', 'EXIT',
             'for_next', 'REMOVE', 'Pay', 'Cancel', 'CANCEL', 'NEW_GAME',
             'EXIT2', 'PAUSE', 'Quit_Playing_', 'Yes2', 'No2', 'CANCEL2',
             'Items', 'Spells', 'Status', 'Equip', 'Order', 'Team', 'Save',
             'Quit', 'Map', 'Volume', 'Buy', 'Sell', 'Inn', 'Hire', 'Exit',
             'CANNOT_SELL', 'Worth', 'Trade_for', 'and_a', 'Worth_Nothing',
             'Sold', 'Trade_for2', 'Joins_for', 'Cannot_Afford', 'Cannot_Hire',
             'Purchased', 'Joined_', 'in_stock', 'Equip_', 'No_Room_In_Party',
             'Replace_Old_Data_', "Who's_Status_", "Who's_Spells_", 'Equip_Who_',
             'Nothing', 'Has_Nothing', 'Cannot_Steal', 'Stole', 'miss', 'fail',
             'learned', 'Found', 'Gained', 'Weak_to', 'Strong_to', 'Absorbs',
             'No_Elemental_Effects', 'has_no_spells', 'Which_Hero_', 'Name_the_Hero',
             'Found_a', 'Found2', 'THE_INN_COSTS', 'You_have', 'CANNOT_RUN_',
             'Level_up_for', 'levels_for', 'and', 'day', 'days', 'hour', 'hours',
             'minute', 'minutes']

dtypes['stt'] = [(name, [('length','B'),('value', 'S%d' % (10 + ((length - 1) * 11)))]) for name, length in zip (STT_NAMES, STT_LENGTHS)]

dtypes['stf'] = [('items', (dtypes['_stf_item'], 50))]

# Debug tools
# =============

def print_array (arr, inline = False):
    """Iterate over fields of dtype, print value of arr[fieldname] for each.

    Normally applied on arrays of shape (1,)"""
    import sys
    import numpy as np
    format = '    %s: %r\n'
    if inline:
        sys.stdout.write ("  - {")
        format = "%s: %r, "
    for field in arr.dtype.descr:
        fieldname = field[0]
        value = arr[fieldname]
        if value.shape == ():
            value = value.tolist()
        elif value.shape[0] == 1: #discard leading ones in shape
            value = value[0]
        if type (value) == np.ndarray:
            value = value.tolist()
        sys.stdout.write  (format % (fieldname, value))
    if inline:
        sys.stdout.write ("}\n")
    sys.stdout.flush()

# FIX also handle big hex strings (eg gfx) here if possible
# done by setting node style = '|'
# and inserting '\n' in the string after every [WIDTH]
# characters
# then after loading, we must strip the '\n'
#
# such strings are always
# serialized as part of a mapping; other mapping
# pairs specify width and height.

# strangely, arr.tolist() on a scalar array returns a scalar not a list.
# also, returns a tuple for complex records.




# Attic
# ======
#
# YAML: identify the object type
# vamji-translate special lo vamji pe special ckiku
#
# invalid characters like binary 0 should be translated to \\00



def escape_strings (data):
    "Recursively convert strings to a YAML-compatible format as needed"

def unescape_strings (data):
    """Recursively convert strings from a YAML-compatible format to
    direct encoding as needed"""

def load_yaml ():
    """intermediate implementation stage.
    Loads vanilla YAML, identifying the object kind
    (from an indicator at the start of the document,
     or explicitly passed)
    and translating 'awkward' fields.
    """
    pass

def save_yaml (object):
    """Save yaml from object with possibly awkward content (eg NULLs)"""
    pass


#>>> fields += fieldlist_to_dtype ('randbattles usebutton menubutton ridingtag')
#>>> fields += fieldlist_to_dtype ('onmount ondismount overridewalls blockedby')
#>>> fields += fieldlist_to_dtype ('mountfrom dismount_to elevation')
#>>> fields += [('reserved', (INT, 18))]



# .. _pylit: http://pylit.berlios.de/examples/index.html
