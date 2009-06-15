Manipulating complex file formats with compound dtypes and memmapping
=====================================================================

in  'scipy.io.npfile' module, you find the following interesting comment:

    You can achieve the same effect as using npfile, using ndarray.tofile
    and numpy.fromfile.
    
    Even better you can use memory-mapped arrays and data-types to map out a
    file format for direct manipulation in NumPy
    
How do we do this? I picked a nice simple example: OHRRPGCE .GEN format.
It has rather a lot of fields which are all signed 16bit integers, little-endian. 
It also has some fields which we can adjust to be aggregate later.

Before running these doctests, I suggest running 'cp --symbolic-link D/* .'
where D is the 'vikings of midgard' rpgdir

Yes, this contains some unix-isms. mainly, if you're running on windows,
making a 'c:\tmp' directory will allow this code to work correctly.

-------------------------------------------
Starting out.. experiments in OHRRPGCE .GEN
-------------------------------------------

>>> import numpy as np
>>> from ohrrpgce import *

OHRRPGCE uses int16's a lot, so let's use an alias for them:

>>> H = np.int16

XXX using {'names': ['foo','bar'],'formats': [H,H,H] }
is more comfortable for most of these formats.
typically, we could just list all the field names, default formats to H,
and then apply corrections as needed.


ignore the BLOAD header.

>>> gen_dtype = np.dtype (dtypes['gen'])
>>> gen_dtype.itemsize
1000

>>> gen = mmap ('viking.gen', gen_dtype, BLOAD_SIZE)
>>> gen
memmap([ (48, 0, 17, 18, 11, 256, 63, [85, 64, 83, 68, 68, 63, 82, 63, 92, 78, 86, 88, 66, 63, 86, 76, 63], 0, [231, 162, 196, 231, 231, 232, 193, 0, 0, 0], 12, 16, 69, 86, 153, 55, 58, 20, 220, 59, 211, 197, 99, 1594, 217, 5, 10, 92, 0, 0, [0, 0, 0, 0], 0, [0, 0, 0, 0], 2, 175, 0, 0, 2, 0, 160, 159, 999, 163, [999, 999, 255, 255, 255, 255, 255, 255, 40, 255, 0, 0], 28, 0, 0, 0, 9, 254, 1, 22, 0, [0, 0, 0, 0, 0, 0, 0], 136, -1, 6, 300, 25, 130, 18, 46, 45, 7, 57, 28, 169, [254, 255, 199, 159, 255, 255, 239, 255, 255, 251, 255, 255, 223, 123, 255, 255, 255, 255, 255, 255, 183, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0, 46, 6, 2, 12, 1, [1, 0, 0, 0], 6, 2, 6, 6, 6, 2, 2, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 8, [374, 1305, 1175, 3156, 1474, 4413, 3227, 4411, 1982, 3898, 258, 199, 612, 1218, 1769, 2623, 1472, 2791, 1165, 156, 1959, 1313, 1245, 3963, 1011, 2678, 663, 2397, 2843, 4192, 2072, 1572, 2446, 883, 2633, 3281, 3506, 1158, 922, 381, 1696, 4179, 3157, 899, 1781, 192, 532, 1016, 1478, 3951, 2827, 2588, 1643, 282, 2289, 4266, 2364, 3010, 1834, 4116, 110, 4077, 3817, 539, 3287, 757, 50, 2757, 1351, 2213, 1564, 2102, 2599, 3334, 2119, 4251, 247, 407, 2836, 2547, 4128, 1007, 874, 1432, 2063, 454, 2823, 1247, 1576, 1651, 1316, 80, 2672, 1767, 2191, 3933, 3460, 355, 699, 3104, 446, 1260, 2997, 3823, 842, 685, 283, 1949, 4262, 442, 726, 1079, 2276, 3178, 4311, 1890, 2061, 1969, 3539, 2831, 2645, 1051, 1761, 1219, 1072, 76, 3197, 3743, 1441, 912, 1989, 4313, 1926, 452, 4314, 482, 3826, 1808, 4262, 1935, 4440, 2901, 829, 61, 23, 3713, 3396, 3190, 619, 106, 1932, 4307, 3041, 1019, 405, 3601, 3771, 1400, 757, 1543], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])], 
      dtype=[('maxmap', '<i2'), ('title', '<i2'), ('titlemusic', '<i2'), ('victorymusic', '<i2'), ('battlemusic', '<i2'), ('passcodeversion', '<i2'), ('passcoderotator', '<i2'), ('newpasscode', '|u1', 17), ('newpasscode_unused', '|u1'), ('oldpasscode', '<i2', 10), ('maxheropic', '<i2'), ('maxenemy1pic', '<i2'), ('maxenemy2pic', '<i2'), ('maxenemy3pic', '<i2'), ('maxnpcpic', '<i2'), ('maxweaponpic', '<i2'), ('maxattackpic', '<i2'), ('maxtileset', '<i2'), ('maxattack', '<i2'), ('maxhero', '<i2'), ('maxenemy', '<i2'), ('maxformation', '<i2'), ('maxpalette', '<i2'), ('maxtextbox', '<i2'), ('maxplotscript', '<i2'), ('newgamescript', '<i2'), ('gameoverscript', '<i2'), ('max_regularscript', '<i2'), ('suspendbits', '<u2'), ('cameramode', '<i2'), ('camera_args', '<i2', 4), ('scriptbackdrop', '<i2'), ('time', '<i2', 4), ('maxvehicle', '<i2'), ('maxtagname', '<i2'), ('loadgamescript', '<i2'), ('textbox_backdrop', '<i2'), ('enemydissolve', '<i2'), ('enablejoy', '<i2'), ('poison', '<i2'), ('stun', '<i2'), ('damagecap', '<i2'), ('mute', '<i2'), ('statcap', '<i2', 12), ('maxsfx', '<i2'), ('masterpal', '<i2'), ('maxmasterpal', '<i2'), ('maxmenu', '<i2'), ('maxmenuitem', '<i2'), ('maxitem', '<i2'), ('max_boxborder', '<i2'), ('maxportrait', '<i2'), ('maxinventory', '<i2'), ('reserved', '<i2', 7), ('oldpassword2_offset', '<i2'), ('oldpassword2_length', '<i2'), ('version', '<i2'), ('startmoney', '<i2'), ('maxshop', '<i2'), ('oldpassword1_offset', '<i2'), ('oldpassword1_length', '<i2'), ('maxbackdrop', '<i2'), ('bitsets', '<u2'), ('startx', '<i2'), ('starty', '<i2'), ('startmap', '<i2'), ('onetimenpc_indexer', '<i2'), ('onetimenpc_bits', '|u1', 130), ('def_deathsfx', '<i2'), ('maxsong', '<i2'), ('acceptsfx', '<i2'), ('cancelsfx', '<i2'), ('choosesfx', '<i2'), ('textboxletter', '<i2'), ('morebitsets', '|u1', 4), ('itemlearnsfx', '<i2'), ('cantlearnsfx', '<i2'), ('buysfx', '<i2'), ('hiresfx', '<i2'), ('sellsfx', '<i2'), ('cantbuysfx', '<i2'), ('cantsellsfx', '<i2'), ('wastedspace', '<i2', 13), ('oldsctable_head', '<u2'), ('oldsctable', '<u2', 160), ('unused', '<u2', 140)])

>>> gen.shape
(1,)

Looks like a huge mess :) thankfully it's really easy to actually access. And below
we print it as a nice YAML format.

Notice this is a [1] array of gen, rather than a scalar ([]).
 
I want to dump in a YAML format, without depending on YAML library...

So here I define a basic checker for correct yaml (ie PyYAML can load it).
I also log the results to a file, so you can inspect them.

EDIT: fix_tuples and dump_memmap moved into 'yamlarray' module from here.

>>> import tempfile
>>> import os
>>> from yamlarray import *
>>> tmpdir = tempfile.mkdtemp('ohrnpy')

>>> logfile = open (os.path.join (tmpdir, 'memmap-fmt-log.yaml'),'w')

>>> def yamlok (ystring):
...     try:
...         import yaml
...     except ImportError:
...         return True # the user doesn't have PyYAML
...     try:
...         loaded = yaml.safe_load (ystring)
...         logfile.write (ystring); logfile.write ('\n')
...     except:
...         logfile.write ('FAILED: '); logfile.write (ystring); logfile.write('\n')
...         return False
...     return True

At the moment though, dump_memmap is broken; so we really want a stub until it's fixed:

>>> def yamlok (ystring):
...     return True


>>> yamlok (dump_memmap (gen))
True


We are finished with it. however 'del somememmappedarray' doesn't work right currently,
so we must just wait for it to be gced, urgh

>>> defpal_dtype = np.dtype (dtypes['defpal%d.bin'])
>>> for i in range (1,8+1):
...     values = mmap ('defpal%d.bin' % i, defpal_dtype)
...     yamlok (dump_memmap (values))
True
True
True
True
True
True
True
True

According to the ohr docs : `UICOLORS.BIN <http://gilgamesh.hamsterrepublic.com/wiki/ohrrpgce/index.php/UICOLORS.BIN>`_ 
We should pop fields according to binsize.bin. to maintain best compatibility.
I skip that here, for brevity.

>>> uicolors_dtype = np.dtype (dtypes['uicolors.bin'])
>>> uicolors_dtype.itemsize
126

>>> uicolors = mmap ('uicolors.bin', uicolors_dtype)

>>> yamlok (dump_memmap (uicolors))
True

We ignore PALETTES.BIN's 2-int header

>>> palettes_dtype = np.dtype (dtypes['palettes.bin'])
>>> palettes_dtype.itemsize
768


We use offset parameter to skip past header:

>>> palettes = mmap ('palettes.bin', palettes_dtype, offset = 2 * 2)
>>> yamlok (dump_memmap (palettes))
True

>>> binsize_fields = dtypes['binsize.bin']
>>> binsizes = mmap ('binsize.bin', binsize_fields)

Now you'll need to pop() fields until the actual binsize dtype has 
``os.path.getsize (binsize) / 2`` fields.

In application code, instead of using a temporary file, you would use a dtype
that looked like:
[('header', HEADER_DTYPE), ('entries', (ENTRY_DTYPE, N))]

Where N is the number of records known to be in the file.

>>> defpass_dtype = dtypes['defpass.bin']
>>> defpass = mmap ('defpass.bin',defpass_dtype)
>>> yamlok (dump_memmap (defpass))
True

(ugly but valid yaml is dumped) -- with large multidimensional arrays this can happen.

An easy remedy is to load and dump it with y.safe_(load|dump):
 y.safe_dump (y.safe_load (uglydump))

You might prefer to dump the above in hex format since it represents bitfields.
a regexp replacement like this:

 re.sub ('([0-9]+)', lambda m: '0x%02x % int (m.expand('\\1')), dump)

will do the trick, provided you don't have numbers >9 in your field names.



fixbits.bin is trivial; a nice interface could be through BitVector (extended
with named bits)

# lookup.bin skipped -- dubious staying value.


>>> sfxdata_dtype = dtypes['sfxdata.bin']
>>> sfxdata = mmap ('sfxdata.bin', sfxdata_dtype)
>>> yamlok (dump_memmap (sfxdata))
True

>>> songdata_dtype = dtypes['songdata.bin']
>>> songdata = np.memmap ('songdata.bin', songdata_dtype)
>>> yamlok (dump_memmap (songdata))
True

Something I didn't cover up till now was loading from the generated YAML file.
This is pretty easy too. 
First, create a recarray of the appropriate size, dtype, and shape:
(it MUST be a recarray, not a normal ndarray)

Here I'm only using the first 4 entries I got from my vikings dump.

>>> destsongdata = np.recarray (shape = (4,), dtype = songdata_dtype)

(until zeroed or overwritten, your array will contain gibberish.
so I zero it here:)
>>> destsongdata[:] = ''

Load your yaml data:

>>> import yaml
>>> yamlized = "[[0, ''], [6, 'Asgard'], [7, 'piano02'], [6, 'song04']]"
>>> loadedsongdata = yaml.safe_load (yamlized)

Convert to tuple format:

>>> loadedsongdata = [tuple (v) for v in loadedsongdata]

Write your data into the array!

>>> destsongdata['name'][:] = loadedsongdata

Just that easy!
Then, if you want to copy a segment of it to the songdata we loaded before,

>>> songdata['name'][4:8] = loadedsongdata

Be aware that the data on disk has now changed! ie. names 4,5,6,7 have been overwritten
with names 0,1,2,3 IN THE FILE (songdata.bin)!



songdata is atypical in that it basically only has one field; most ohr
datatypes have several. Typically when you load a yaml dump like::

 background           : 0
 menuitem             : 7
 disableditem         : 8
 selecteditem         : [14, 15]
 selecteddisabled     : [6, 7]
 highlight            : [1, 2]
 timebar              : 18
 timebarfull          : 21
 healthbar            : 51
 healthbarflash       : 53
 text                 : 15
 outline              : 240
 description          : 10
 gold                 : 14
 shadow               : 240
 textbox              : [[18, 28], [34, 44], [50, 60], [66, 76], [82, 92], [98, 108], [114, 124], [130, 140], [146, 156], [162, 172], [178, 188], [194, 204], [210, 220], [226, 236], [242, 252]]
 textboxframe         : [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]

you'll get something like::

 {'background': 0,
 'description': 10,
 'disableditem': 8,
 'gold': 14,
 'healthbar': 51,
 'healthbarflash': 53,
 'highlight': [1, 2],
 'menuitem': 7,
 'outline': 240,
 'selecteddisabled': [6, 7],
 'selecteditem': [14, 15],
 'shadow': 240,
 'text': 15,
 'textbox': [[18, 28],
             [34, 44],
             [50, 60],
             [66, 76],
             [82, 92],
             [98, 108],
             [114, 124],
             [130, 140],
             [146, 156],
             [162, 172],
             [178, 188],
             [194, 204],
             [210, 220],
             [226, 236],
             [242, 252]],
 'textboxframe': [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
 'timebar': 18,
 'timebarfull': 21}

as your output.
This is very convenient, we can assign all those fields pretty easy:

>>> def convert2tuples (_list):
...     result = []
...     for value in _list:
...         if type (value) == list:
...             result.append (tuple (v))
...         else:
...             result.append (tuple (v))
...     return result

>>> def assign_recarray (arr, dict):
...     for name, value in dict.items():
...         #automangle list->tuple:
...         if type (value) == list:
...             value = convert2tuples (value)
...         arr[name] = value

>>> assign_recarray (uicolors, loaded_ui_yaml)

There are 2 ways to view your data: 
1. in terms of planes (all the timebar data, then all the timebarfull data..)

   arr['name']

2. in terms of position (all the everything data for only a chunk of the array)

   arr[:4]

At this point, I checked this .rst file into git.

Initial checkin of this file included support for:
* palettes.bin 
* gen
* defpal*.bin
* defpass.bin
* uicolors.bin
* binsize.bin



VEH, TMN, MXS, TIL and..
------------------------


>>> veh_dtype = np.dtype (dtypes['veh'])
>>> veh_dtype.itemsize
80

>>> veh = mmap ('viking.veh', veh_dtype)
>>> yamlok (dump_memmap (veh))
True

>>> tmn_dtype = dtypes['tmn']
>>> tmn = mmap ('viking.tmn', tmn_dtype)
>>> yamlok (dump_memmap (tmn[:16]))
True

# ugly dump (because of crazy int16-based string encoding.)

fixing up is possible, as long as you unfix when loading

>>> mxs_dtype = dtypes ['mxs']
>>> mxs = mmap ('viking.mxs', mxs_dtype)
>>> til = mmap ('viking.til', mxs_dtype)

I didn't dump mxs or til because even a single record prints out huge.

MXS, TIL and TMN are some types that could do with a 'nice' wrapper class (allowing planar or
non-int16 access)

>>> def pt_shape (width, height, frames):
...     return (frames, width, height/2)

PTx are easy to load; I'll load the weapon gfx

>>> size = 12*24*2
>>> pt5 = np.memmap ('viking.pt5', dtype = [('pixels',(np.uint8, size))], mode = 'r')

Why did I do that? because if I specified a shape, it would only consider exactly that many
records. If you care to check file size, you can specify a proper shape,
rather than calculating it afterwards here. Checking filesize is somewhat more efficient
than this approach.

>>> pt5 = pt5['pixels'].astype (np.uint8)
>>> pt5.shape = (pt5.size / size, 2, 24, 12,)
>>> pt5[4]
memmap([[[  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,  12,  76],
        [  0,   0,   0,   0,   0,   0,   0,   0,  37, 192,  36, 183],
        [  0,   0,   0,   0,   0,   0,   0,   3, 108, 130,  88, 124],
        [  0,   0,   0,   0,   0,   0,   0,  54,  58,  88,  85,  32],
        [  0,   0,   0,   0,   0,   0,   3,  99, 175, 108, 130,   0],
        [  0,   0,   0,   0,   0,   0,  54,  58, 246,  58,  88, 192],
        [  0,   0,   0,   0,   0,   3, 102, 175,  99, 175, 108,  80],
        [  0,   0,   0,   0,   0,  54, 106, 246,  58, 246,  58,  32],
        [  0,   0,   0,   0, 195, 170, 255, 102, 175,  99, 175,   0],
        [  0,   0,   0,  12, 175, 255,  54, 106, 246,  58, 240,   0],
        [  0,   0,   0,   0,   0, 195, 106, 255, 102, 175,   0,   0],
        [  0,   0,   0,   0,  12, 175, 255,  54, 106, 240,   0,   0],
        [  0,   0,   0,   0,   0,   0, 195, 106, 255,   0,   0,   0],
        [  0,   0,   0,   0,   0,  12, 175, 255,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0]],
<BLANKLINE>
       [[  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0, 192,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0, 172,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0, 192, 243,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0, 172, 250,  48,   0,   0,   0],
        [  0,   0,   0,   0,   0, 192, 243, 250,  99,   0,   0,   0],
        [  0,   0,   0,   0,   0, 172, 246,  63, 102,  48,   0,   0],
        [  0,   0,   0,   0,   0, 243, 250, 111, 166,  99,   0,   0],
        [  0,   0,   0,   0,   0, 246,  63, 102, 250,  54,  48,   0],
        [  0,   0,   0,   0,   0, 250, 111, 166, 111, 163,  99,   0],
        [  0,   0,   0,   0,   0,  15, 102, 250,  54, 250,  54,  32],
        [  0,   0,   0,   0,   0,  15, 166, 111, 163, 111, 172,  80],
        [  0,   0,   0,   0,   0,   0, 250,  54, 250,  54,  88, 192],
        [  0,   0,   0,   0,   0,   0,  15, 163, 111, 172, 130,   0],
        [  0,   0,   0,   0,   0,   0,   0, 250,  54,  88,  85,  32],
        [  0,   0,   0,   0,   0,   0,   0,  15, 172, 130,  88,  76],
        [  0,   0,   0,   0,   0,   0,   0,   0,  37, 192,  39, 180],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,  12, 124]]], dtype=uint8)

dump_memmap won't work on that, since it's a simple dtype. 
We can simply dump the result of tolist(), though -- it will be valid YAML::

 pt5[4].tolist()

A bit ugly though; what happens if we use yaml to load and redump it?
Quite nice. In fact, with the hexlification regex-trick, it's fairly readable.

For modification, you may want to  unpack them to 1byte/pixel.

>>> part1 = pt5[4] & 0xf
>>> part2 = (pt5[4] & 0xf0) >> 4
>>> unpacked_frames = np.zeros (shape = (2*24*24), dtype = np.uint8)
>>> unpacked_frames.flat[0::2] = part1
>>> unpacked_frames.flat[1::2] = part2
>>> unpacked_frames.shape = (2,24,24)
>>> unpacked_frames
array([[[ 0,  0,  0, ...,  0, 12,  4],
        [ 0,  0,  0, ...,  2,  7, 11],
        [ 0,  0,  0, ...,  5, 12,  7],
        ..., 
        [ 0,  0,  0, ...,  0,  0,  0],
        [ 0,  0,  0, ...,  0,  0,  0],
        [ 0,  0,  0, ...,  0,  0,  0]],
<BLANKLINE>
       [[ 0,  0,  0, ...,  0,  0,  0],
        [ 0,  0,  0, ...,  0,  0,  0],
        [ 0,  0,  0, ...,  0,  0,  0],
        ..., 
        [ 0,  0,  0, ...,  5, 12,  4],
        [ 0,  0,  0, ...,  2,  4, 11],
        [ 0,  0,  0, ...,  0, 12,  7]]], dtype=uint8)

from::
 124 & 0xf == 12
 (124 >> 4) & 0xf == 7

You can see that the last two pixels in the last column are 12 and 7.
When the image is displayed, those pixels will be like this::

 .v--- here
 4C
 B7 <- bottom right corner

You need to keep in mind that the last dimension is Y, not the usual X; that's why
12 and 7 are the last two pixels in the rightmost column, rather than the last 
two pixels in the bottommost row.

When repacking frames:

>>> repacked_frames = unpacked_frames[...,::2] | ( unpacked_frames[...,1::2] << 4)
>>> repacked_frames 
array([[[  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,  12,  76],
        [  0,   0,   0,   0,   0,   0,   0,   0,  37, 192,  36, 183],
        [  0,   0,   0,   0,   0,   0,   0,   3, 108, 130,  88, 124],
        [  0,   0,   0,   0,   0,   0,   0,  54,  58,  88,  85,  32],
        [  0,   0,   0,   0,   0,   0,   3,  99, 175, 108, 130,   0],
        [  0,   0,   0,   0,   0,   0,  54,  58, 246,  58,  88, 192],
        [  0,   0,   0,   0,   0,   3, 102, 175,  99, 175, 108,  80],
        [  0,   0,   0,   0,   0,  54, 106, 246,  58, 246,  58,  32],
        [  0,   0,   0,   0, 195, 170, 255, 102, 175,  99, 175,   0],
        [  0,   0,   0,  12, 175, 255,  54, 106, 246,  58, 240,   0],
        [  0,   0,   0,   0,   0, 195, 106, 255, 102, 175,   0,   0],
        [  0,   0,   0,   0,  12, 175, 255,  54, 106, 240,   0,   0],
        [  0,   0,   0,   0,   0,   0, 195, 106, 255,   0,   0,   0],
        [  0,   0,   0,   0,   0,  12, 175, 255,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0]],
<BLANKLINE>
       [[  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0, 192,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0, 172,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0, 192, 243,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0, 172, 250,  48,   0,   0,   0],
        [  0,   0,   0,   0,   0, 192, 243, 250,  99,   0,   0,   0],
        [  0,   0,   0,   0,   0, 172, 246,  63, 102,  48,   0,   0],
        [  0,   0,   0,   0,   0, 243, 250, 111, 166,  99,   0,   0],
        [  0,   0,   0,   0,   0, 246,  63, 102, 250,  54,  48,   0],
        [  0,   0,   0,   0,   0, 250, 111, 166, 111, 163,  99,   0],
        [  0,   0,   0,   0,   0,  15, 102, 250,  54, 250,  54,  32],
        [  0,   0,   0,   0,   0,  15, 166, 111, 163, 111, 172,  80],
        [  0,   0,   0,   0,   0,   0, 250,  54, 250,  54,  88, 192],
        [  0,   0,   0,   0,   0,   0,  15, 163, 111, 172, 130,   0],
        [  0,   0,   0,   0,   0,   0,   0, 250,  54,  88,  85,  32],
        [  0,   0,   0,   0,   0,   0,   0,  15, 172, 130,  88,  76],
        [  0,   0,   0,   0,   0,   0,   0,   0,  37, 192,  39, 180],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,  12, 124]]], dtype=uint8)


if you had transposed() it to get the usual [Y][X] ordering, you would
need to transpose it back, before using the above operation.


after you read and discard the header, the following will load
.t??, .p??, e??

If it's .t, you need to use::
 shape = (nlayers, height, width)

else::
 shape = (height, width)

then ::
 nelems = reduce (lambda a,b: a*b, shape)
 map = np.memmap ('vikings.t00', dtype = [('tiles', (np.uint8, nelems))], mode = 'r')
 map.shape = shape

there are bitsets in MAP file which will indicate what the appropriate 
value is for a particular map. 

------------------
Planar bizarreness
------------------

For some formats, like DOR, you have all the x, all the y, all the flags in 100-element
planar format.

>>> doorlink_dtype = dtypes['d']
>>> doorlinks = mmap ('viking.d00', doorlink_dtype, offset = 7)
>>> yamlok (dump_memmap (doorlinks))
True

>>> efs_dtype = dtypes['efs']
>>> efs = mmap ('viking.efs', efs_dtype)
>>> yamlok (dump_memmap (efs[0:2]))
True


>>> formation_dtype = dtypes['for']
>>> form = mmap ('viking.for', formation_dtype)
>>> yamlok (dump_memmap (form[:2]))
True

Until now, I haven't shown creating new files, or even modifying them.
I'll create a new formation file.
Notice I must explicitly specify the shape and mode:

>>> for_name = os.path.join (tmpdir, 'my.for')
>>> form_dest = np.memmap (for_name, dtype = formation_dtype, shape = form[:2].shape, mode = "write")
>>> form_dest[:] = form[:2]

Now we know that 2 formations take up 80*2 == 160 bytes:

>>> os.path.getsize (for_name)
160L

SWEET :)

>>> browse_dtype = dtypes['browse.txt']
>>> browse = np.memmap ('browse.txt', dtype = browse_dtype)
>>> yamlok (dump_memmap (browse))
True

we get two strings with junk, usually. Unfortunately this junk does not fit well into YAML.
Fortunately, it's easy to fill the remainder of the strings with zeros.
see ohrrpgce.fixstringjunk()

We can also open files for simultaneous reading and writing -- in fact, this is 
the default.

>>> fix_stringjunk (browse)
>>> yamlok (dump_memmap (browse))
True

Whoops! I forgot I had opened the original file without write permission!
I'll go back and fix that.. 
and wipe out the junk bytes from the file in the process above!


----------
Combatants
----------

combatants, as well as attack data, share a datatype for storing stats:

>>> hero_dtype = dtypes['dt0']
>>> print hero_dtype
{'names': ['name', 'battlesprite', 'battlepalette', 'walksprite', 'walkpalette', 'defaultlevel', 'defaultweapon', 'stats', 'spells', 'portrait', 'bitsets', 'spelllist_name', 'portrait_palette', 'spelllist_type', 'have_tag', 'alive_tag', 'leader_tag', 'active_tag', 'maxnamelength', 'handcoord', 'standframe', 'stepframe', 'attackaframe', 'attackbframe', 'castframe', 'hurtframe', 'weakframe', 'deadframe', 'dead2frame', 'targettingframe', 'victoryaframe', 'victorybframe', 'unused'], 'formats': [[('length', <type 'numpy.uint16'>), ('data', (<type 'numpy.character'>, 32))], <type 'numpy.int16'>, <type 'numpy.int16'>, <type 'numpy.int16'>, <type 'numpy.int16'>, <type 'numpy.int16'>, <type 'numpy.int16'>, [('hp', (<type 'numpy.int16'>, 2)), ('mp', (<type 'numpy.int16'>, 2)), ('str', (<type 'numpy.int16'>, 2)), ('acc', (<type 'numpy.int16'>, 2)), ('def', (<type 'numpy.int16'>, 2)), ('dog', (<type 'numpy.int16'>, 2)), ('mag', (<type 'numpy.int16'>, 2)), ('wil', (<type 'numpy.int16'>, 2)), ('spd', (<type 'numpy.int16'>, 2)), ('ctr', (<type 'numpy.int16'>, 2)), ('foc', (<type 'numpy.int16'>, 2)), ('xhits', (<type 'numpy.int16'>, 2))], ([('attack', <type 'numpy.int16'>), ('level', <type 'numpy.int16'>)], (4, 24)), <type 'numpy.int16'>, (<type 'numpy.uint8'>, 6), ([('length', <type 'numpy.int16'>), ('value', (<type 'numpy.character'>, 20))], 4), <type 'numpy.int16'>, (<type 'numpy.int16'>, 4), <type 'numpy.int16'>, <type 'numpy.int16'>, <type 'numpy.int16'>, <type 'numpy.int16'>, <type 'numpy.int16'>, ([('x', <type 'numpy.int16'>), ('y', <type 'numpy.int16'>)], 2), <type 'numpy.int16'>, <type 'numpy.int16'>, <type 'numpy.int16'>, <type 'numpy.int16'>, <type 'numpy.int16'>, <type 'numpy.int16'>, <type 'numpy.int16'>, <type 'numpy.int16'>, <type 'numpy.int16'>, <type 'numpy.int16'>, <type 'numpy.int16'>, <type 'numpy.int16'>, (<type 'numpy.int16'>, 5)]}

>>> hero_dtype = np.dtype (hero_dtype)
>>> hero_dtype.itemsize
636
>>> hero = mmap ('viking.dt0', hero_dtype)
>>> yamlok (dump_memmap (hero[:2]))
True

>>> item_dtype = dtypes['itm']
>>> item_dtype = np.dtype (item_dtype)
>>> item_dtype.itemsize
200
>>> item = mmap ('viking.itm', item_dtype)
>>> yamlok (dump_memmap (item[:4]))
True

>>> tap_dtype = dtypes['tap']
>>> tap = mmap ('viking.tap', tap_dtype)
>>> yamlok (dump_memmap (tap[:2]))
True

Just for convenience, here's a LUT mapping action type to string name:

>>> tap_lookup = "end up down right left stop continueiftag".split()

Which I'll use to translate tap[1].

>>> zip ([tap_lookup[v] for v in tap[1]['actiontype']], tap[1]['actionparam'])
[('right', 1), ('stop', 2), ('right', 1), ('stop', 2), ('left', 1), ('stop', 2), ('left', 1), ('stop', 2), ('end', 0)]

It's then obvious that this is a simple pingpong animation pattern.

>>> shop_dtype = dtypes['sho']

>>> shop = mmap ('viking.sho', shop_dtype)
>>> yamlok (dump_memmap (shop[:2]))
True

>>> len(shop)
26

#XXX respect BINSIZE.BIN size recorded for this file

>>> shopstuffi_dtype = np.dtype (dtypes['_stf_item'])
>>> shopstuffi_dtype.itemsize
84

>>> shopstuff_dtype = [('items', (shopstuffi_dtype, 50))]
>>> shopstuff_dtype = np.dtype (dtypes['stf'])
>>> shopstuff_dtype.itemsize
4200

The way OHRRPGCE accesses shopstuff does not guarantee the last set being complete 
(my test data has complete data for 24 shops and only 17 items for the 25th shop).
The nicest behaviour IMO is to pad to a multiple of 50 records before opening.


>>> nrecords = pad ('viking.stf', shopstuffi_dtype.itemsize, 50)
>>> nrecords % 50
0

>>> shopstuff = mmap ('viking.stf', shopstuff_dtype)
>>> yamlok (dump_memmap (shopstuff[0]))
True

newer OHRRPGCE files don't depend too much on this format, still, it's easy to support.

>>> masentry_dtype = np.dtype (dtypes['mas'])

#>>> mas_dtype = np.dtype ([BLOAD_HEADER, ('palette', maspalette_dtype), ('wasted', ('B', 7))])
>>> mas = mmap ('viking.mas', masentry_dtype, offset = 7, shape = 256)
>>> mas.shape
(256,)

>>> yamlok (dump_memmap (mas))
True

>>> mn_dtype = np.dtype (dtypes['mn'])
>>> mn = mmap ('viking.mn', mn_dtype)
>>> yamlok (dump_memmap (mn))
True

# is there some way to alias herolevel to selltype? the same field has this different
# meaning according to the kind of item.

>>> npcdefs_dtype = dtypes['n'] 
>>> npcdefs_dtype = np.dtype (npcdefs_dtype)
>>> npcdefs_dtype.itemsize
3007

>>> npcdefs = mmap ('viking.n01', npcdefs_dtype)
>>> yamlok (dump_memmap (npcdefs[0:16]))
True

>>> import os
>>> fixbits_size = os.path.getsize('fixbits.bin')

Make a 'memmapped' bitsets class:


>>> fixbits = fixBits ('fixbits.bin')
>>> fixbits
fixBits ('fixbits.bin', attackitems = 1, weappoints = 1, stuncancel = 1, defaultdissolve = 1, defaultdissolveenemy = 1, pushnpcbug_compat = 1, default_maxitem = 1, blankdoorlinks = 1, shopsounds = 1, extended_npcs = 1, heroportrait = 1, textbox_portrait = 1, npclocation_format = 0)


>>> archinym = archiNym ('archinym.lmp')
>>> archinym
archiNym ('archinym.lmp', 'Viking', 'OHRRPGCE Editor: serendipity 20060218')

>>> archinym.prefix
'Viking'


>>> say_dtype = np.dtype (dtypes['say'])
>>> say_dtype.itemsize
410

>>> say = mmap ('viking.say', say_dtype)
>>> yamlok (dump_memmap (say[0:16]))
True


>>> plotscr_dtype = dtypes['plotscr.lst'] 
>>> plotscr = mmap ('plotscr.lst', plotscr_dtype)
>>> yamlok (dump_memmap (plotscr[:16]))
True

>>> door_dtype = dtypes['dox']
>>> door = mmap ('viking.dox', door_dtype)
>>> yamlok (dump_memmap (door[:16]))
True

>>> old_npcloc_dtype = dtypes['l']

The following wasn't migrated to ohrrpgce.py because it is just a planned format revision, not a format
currently used.

>>> npcloc_dtype = [('loc', (fieldlist_to_dtype ('id x y dir'), 300))]
>>> npcloc_dtype = [BLOAD_HEADER ] + npcloc_dtype
>>> npcloc_dtype = np.dtype (npcloc_dtype)
>>> npcloc_dtype.itemsize
2407

>>> npcloc = mmap ('viking.l00', old_npcloc_dtype)
>>> npcloc[0]
([253, 153, 153, 0, 0, 184, 11], [45, 14, 19, 10, 39, 32, 36, 23, 15, 20, 23, 25, 21, 20, 24, 25, 22, 18, 18, 19, 19, 19, 21, 21, 21, 22, 22, 21, 24, 25, 25, 26, 24, 25, 24, 26, 27, 25, 23, 38, 11, 30, 46, 47, 45, 45, 46, 46, 47, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [28, 39, 12, 15, 32, 43, 32, 41, 39, 8, 13, 15, 15, 14, 14, 17, 17, 16, 14, 15, 17, 18, 18, 16, 14, 15, 12, 12, 12, 12, 13, 15, 15, 14, 17, 17, 18, 18, 18, 40, 30, 37, 28, 28, 29, 30, 29, 30, 28, 21, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 16, 17, 18, 20, 19, 21, 21, 22, 22, 22, 23, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [2, 2, 2, 2, 2, 2, 1, 0, 0, 2, 2, 3, 1, 2, 1, 3, 0, 0, 1, 1, 3, 2, 0, 3, 0, 1, 3, 1, 1, 3, 0, 3, 1, 2, 0, 2, 2, 3, 1, 3, 1, 1, 1, 3, 2, 2, 2, 2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])


# XXX we need a function that looks at BINSIZE info and automatically pops records beyond the
# specified endpoint.

-----------------
more helper funcs
-----------------

ohrrpgce.(set|get)_str(8|16) are useful for manipulating OHR string values.
They used to be defined here.

The following could be improved. So could the original strings used in the editor.


>>> stt_dtype = np.dtype (dtypes['stt'])#stt_dtype)
>>> stt_dtype.itemsize
1760

 STT uses random access, so the last record could be partially specified.
 hence auto-padding is needed. 

I haven't tested yet, I suspect assigning to fields of double or triple length
may require some mangling every 11 letters.

>>> stt_nrecords = pad ('viking.stt', 11)

STT is fairly horrendous, with junk bytes everywhere. So let's clean up.
Note that if you want to read first, you need to open with 'r+' mode,
not 'w+'
>>> stt = np.memmap ('viking.stt', mode = "r+", dtype = stt_dtype)
>>> fix_stringjunk (stt)
>>> stt
memmap([ ((2, 'HP'), (2, 'MP'), (8, '\x88 Attack'), (10, '\x8d Accuracy'), (9, '\xa5 Attacks'), (9, '\x95 Defense'), (9, '\x92 Evasion'), (7, '\x85 Vigor'), (7, '\x8e Speed'), (7, '\xb2 Giant'), (10, '\xb5 Humanoid'), (8, '\xa1 Undead'), (8, '\xb4 Dragon'), (7, '\xb1 Golem'), (7, '\xb3 Beast'), (6, '\x99 Hero'), (9, '\xa6 Organic'), (6, '\xae Fire'), (5, '\xaf Ice'), (10, '\xb0 Electric'), (7, '\xa1 Death'), (8, '\xa0 Status'), (7, 'PROVOKE'), (0, ''), (10, '\x85 Recovery'), (6, '\xb7 Head'), (6, '\xb8 Body'), (6, '\xb9 Hand'), (7, '\x90 Extra'), (7, '\x82 Magic'), (8, '\x83 Wisdom'), (6, '\x84 Soul'), (1, '$'), (10, 'Experience'), (4, 'Item'), (4, 'DONE'), (8, 'AUTOSORT'), (5, 'TRASH'), (8, '\xb6 Weapon'), (8, '-REMOVE-'), (6, '-EXIT-'), (7, 'Discard'), (6, 'Cannot'), (5, 'Level'), (3, 'Yes'), (2, 'No'), (4, 'EXIT'), (8, 'for next'), (6, 'REMOVE'), (3, 'Pay'), (6, 'Cancel'), (8, '(CANCEL)'), (8, 'NEW GAME'), (4, 'EXIT'), (5, 'PAUSE'), (13, 'Quit Playing?'), (3, 'Yes'), (2, 'No'), (6, 'CANCEL'), (5, 'ITEMS'), (6, 'SPELLS'), (6, 'STATUS'), (5, 'EQUIP'), (5, 'ORDER'), (4, 'TEAM'), (4, 'SAVE'), (4, 'QUIT'), (3, 'MAP'), (6, 'VOLUME'), (3, 'Buy'), (4, 'Sell'), (3, 'Inn'), (4, 'Hire'), (4, 'Exit'), (11, 'CANNOT SELL'), (5, 'Worth'), (9, 'Trade for'), (5, 'and a'), (13, 'Worth Nothing'), (4, 'Sold'), (9, 'Trade for'), (9, 'Joins for'), (13, 'Cannot Afford'), (11, 'Cannot Hire'), (9, 'Purchased'), (7, 'Joined!'), (8, 'in stock'), (6, 'Equip:'), (16, 'No Room In Party'), (17, 'Replace Old Data?'), (13, "Who's Status?"), (13, "Who's Spells?"), (10, 'Equip Who?'), (7, 'Nothing'), (11, 'Has Nothing'), (12, 'Cannot Steal'), (5, 'Stole'), (4, 'miss'), (4, 'fail'), (7, 'learned'), (5, 'Found'), (6, 'Gained'), (7, 'Weak to'), (9, 'Strong to'), (7, 'Absorbs'), (20, 'No Elemental Effects'), (13, 'has no spells'), (11, 'Which Hero?'), (13, 'Name the Hero'), (7, 'Found a'), (5, 'Found'), (13, 'THE INN COSTS'), (8, 'You have'), (11, 'CANNOT RUN!'), (12, 'Level up for'), (10, 'levels for'), (3, 'and'), (3, 'day'), (4, 'days'), (4, 'hour'), (5, 'hours'), (6, 'minute'), (7, 'minutes'))], 
      dtype=[('Health_Points', [('length', '|u1'), ('value', '|S10')]), ('Spell_Points', [('length', '|u1'), ('value', '|S10')]), ('Attack_Power', [('length', '|u1'), ('value', '|S10')]), ('Accuracy', [('length', '|u1'), ('value', '|S10')]), ('Extra_Hits', [('length', '|u1'), ('value', '|S10')]), ('Blocking_Power', [('length', '|u1'), ('value', '|S10')]), ('Dodge_Rate', [('length', '|u1'), ('value', '|S10')]), ('Counter_Rate', [('length', '|u1'), ('value', '|S10')]), ('Speed', [('length', '|u1'), ('value', '|S10')]), ('Enemy_Type_1', [('length', '|u1'), ('value', '|S10')]), ('Enemy_Type_2', [('length', '|u1'), ('value', '|S10')]), ('Enemy_Type_3', [('length', '|u1'), ('value', '|S10')]), ('Enemy_Type_4', [('length', '|u1'), ('value', '|S10')]), ('Enemy_Type_5', [('length', '|u1'), ('value', '|S10')]), ('Enemy_Type_6', [('length', '|u1'), ('value', '|S10')]), ('Enemy_Type_7', [('length', '|u1'), ('value', '|S10')]), ('Enemy_Type_8', [('length', '|u1'), ('value', '|S10')]), ('Elemental_1', [('length', '|u1'), ('value', '|S10')]), ('Elemental_2', [('length', '|u1'), ('value', '|S10')]), ('Elemental_3', [('length', '|u1'), ('value', '|S10')]), ('Elemental_4', [('length', '|u1'), ('value', '|S10')]), ('Elemental_5', [('length', '|u1'), ('value', '|S10')]), ('Elemental_6', [('length', '|u1'), ('value', '|S10')]), ('Elemental_7', [('length', '|u1'), ('value', '|S10')]), ('Elemental_8', [('length', '|u1'), ('value', '|S10')]), ('Armor_1', [('length', '|u1'), ('value', '|S10')]), ('Armor_2', [('length', '|u1'), ('value', '|S10')]), ('Armor_3', [('length', '|u1'), ('value', '|S10')]), ('Armor_4', [('length', '|u1'), ('value', '|S10')]), ('Spell_Skill', [('length', '|u1'), ('value', '|S10')]), ('Spell_Block', [('length', '|u1'), ('value', '|S10')]), ('Spell_cost__', [('length', '|u1'), ('value', '|S10')]), ('Money', [('length', '|u1'), ('value', '|S10')]), ('Experience', [('length', '|u1'), ('value', '|S10')]), ('Item', [('length', '|u1'), ('value', '|S10')]), ('DONE', [('length', '|u1'), ('value', '|S10')]), ('AUTOSORT', [('length', '|u1'), ('value', '|S10')]), ('TRASH', [('length', '|u1'), ('value', '|S10')]), ('Weapon', [('length', '|u1'), ('value', '|S10')]), ('_REMOVE_', [('length', '|u1'), ('value', '|S10')]), ('_EXIT_', [('length', '|u1'), ('value', '|S10')]), ('Discard', [('length', '|u1'), ('value', '|S10')]), ('Cannot', [('length', '|u1'), ('value', '|S10')]), ('Level', [('length', '|u1'), ('value', '|S10')]), ('Yes', [('length', '|u1'), ('value', '|S10')]), ('No', [('length', '|u1'), ('value', '|S10')]), ('EXIT', [('length', '|u1'), ('value', '|S10')]), ('for_next', [('length', '|u1'), ('value', '|S10')]), ('REMOVE', [('length', '|u1'), ('value', '|S10')]), ('Pay', [('length', '|u1'), ('value', '|S10')]), ('Cancel', [('length', '|u1'), ('value', '|S10')]), ('CANCEL', [('length', '|u1'), ('value', '|S10')]), ('NEW_GAME', [('length', '|u1'), ('value', '|S10')]), ('EXIT2', [('length', '|u1'), ('value', '|S10')]), ('PAUSE', [('length', '|u1'), ('value', '|S10')]), ('Quit_Playing_', [('length', '|u1'), ('value', '|S21')]), ('Yes2', [('length', '|u1'), ('value', '|S10')]), ('No2', [('length', '|u1'), ('value', '|S10')]), ('CANCEL2', [('length', '|u1'), ('value', '|S10')]), ('Items', [('length', '|u1'), ('value', '|S10')]), ('Spells', [('length', '|u1'), ('value', '|S10')]), ('Status', [('length', '|u1'), ('value', '|S10')]), ('Equip', [('length', '|u1'), ('value', '|S10')]), ('Order', [('length', '|u1'), ('value', '|S10')]), ('Team', [('length', '|u1'), ('value', '|S10')]), ('Save', [('length', '|u1'), ('value', '|S10')]), ('Quit', [('length', '|u1'), ('value', '|S10')]), ('Map', [('length', '|u1'), ('value', '|S10')]), ('Volume', [('length', '|u1'), ('value', '|S10')]), ('Buy', [('length', '|u1'), ('value', '|S10')]), ('Sell', [('length', '|u1'), ('value', '|S10')]), ('Inn', [('length', '|u1'), ('value', '|S10')]), ('Hire', [('length', '|u1'), ('value', '|S10')]), ('Exit', [('length', '|u1'), ('value', '|S10')]), ('CANNOT_SELL', [('length', '|u1'), ('value', '|S21')]), ('Worth', [('length', '|u1'), ('value', '|S21')]), ('Trade_for', [('length', '|u1'), ('value', '|S21')]), ('and_a', [('length', '|u1'), ('value', '|S10')]), ('Worth_Nothing', [('length', '|u1'), ('value', '|S21')]), ('Sold', [('length', '|u1'), ('value', '|S10')]), ('Trade_for2', [('length', '|u1'), ('value', '|S21')]), ('Joins_for', [('length', '|u1'), ('value', '|S21')]), ('Cannot_Afford', [('length', '|u1'), ('value', '|S21')]), ('Cannot_Hire', [('length', '|u1'), ('value', '|S21')]), ('Purchased', [('length', '|u1'), ('value', '|S21')]), ('Joined_', [('length', '|u1'), ('value', '|S21')]), ('in_stock', [('length', '|u1'), ('value', '|S21')]), ('Equip_', [('length', '|u1'), ('value', '|S10')]), ('No_Room_In_Party', [('length', '|u1'), ('value', '|S21')]), ('Replace_Old_Data_', [('length', '|u1'), ('value', '|S21')]), ("Who's_Status_", [('length', '|u1'), ('value', '|S21')]), ("Who's_Spells_", [('length', '|u1'), ('value', '|S21')]), ('Equip_Who_', [('length', '|u1'), ('value', '|S21')]), ('Nothing', [('length', '|u1'), ('value', '|S10')]), ('Has_Nothing', [('length', '|u1'), ('value', '|S32')]), ('Cannot_Steal', [('length', '|u1'), ('value', '|S32')]), ('Stole', [('length', '|u1'), ('value', '|S32')]), ('miss', [('length', '|u1'), ('value', '|S21')]), ('fail', [('length', '|u1'), ('value', '|S21')]), ('learned', [('length', '|u1'), ('value', '|S10')]), ('Found', [('length', '|u1'), ('value', '|S10')]), ('Gained', [('length', '|u1'), ('value', '|S10')]), ('Weak_to', [('length', '|u1'), ('value', '|S10')]), ('Strong_to', [('length', '|u1'), ('value', '|S10')]), ('Absorbs', [('length', '|u1'), ('value', '|S10')]), ('No_Elemental_Effects', [('length', '|u1'), ('value', '|S32')]), ('has_no_spells', [('length', '|u1'), ('value', '|S21')]), ('Which_Hero_', [('length', '|u1'), ('value', '|S21')]), ('Name_the_Hero', [('length', '|u1'), ('value', '|S21')]), ('Found_a', [('length', '|u1'), ('value', '|S21')]), ('Found2', [('length', '|u1'), ('value', '|S21')]), ('THE_INN_COSTS', [('length', '|u1'), ('value', '|S21')]), ('You_have', [('length', '|u1'), ('value', '|S21')]), ('CANNOT_RUN_', [('length', '|u1'), ('value', '|S21')]), ('Level_up_for', [('length', '|u1'), ('value', '|S21')]), ('levels_for', [('length', '|u1'), ('value', '|S21')]), ('and', [('length', '|u1'), ('value', '|S10')]), ('day', [('length', '|u1'), ('value', '|S10')]), ('days', [('length', '|u1'), ('value', '|S10')]), ('hour', [('length', '|u1'), ('value', '|S10')]), ('hours', [('length', '|u1'), ('value', '|S10')]), ('minute', [('length', '|u1'), ('value', '|S10')]), ('minutes', [('length', '|u1'), ('value', '|S10')])])

In this case, it's most logical to have no named fields, just a simple 
multidimensional array as the dtype.
This means that fnt will be of shape (1, 256, 8) and dtype 'B'. It's handy :)

>>> fnt_dtype = dtypes['fnt']

 FNT is also known as OHF when exported

>>> fnt = mmap ('viking.fnt', fnt_dtype, offset = 7)

 One quirk I didn't notice until now: because memmap is oriented around multiple
 records, when we give a dtype as above, we actually get a (1,) shaped array. 
 For formats with only one record, we want a ()-shaped array -- ie a 'scalar' of
 the specified dtype.
 Therefore:

>>> fnt.shape
(1, 256, 8)
>>> fnt.shape = fnt.shape [1:]
>>> yamlok (dump_memmap (fnt))
Traceback (most recent call last):
   ...
TypeError: 'NoneType' object is not iterable

The above exception happens because dump_memmap doesn't currently
handle simpler dtypes.

>>> testchar = ord ('A')

>>> fnt.dtype
dtype('uint8')

>>> len (fnt)
256

>>> fnt.shape
(256, 8)

>>> fnt[testchar]
memmap([120, 124,  22,  19,  22, 124, 120,   0], dtype=uint8)

>>> unpacked = np.rot90 (np.unpackbits (fnt[testchar]).reshape (8,8), 1)
>>> unpacked
memmap([[0, 0, 0, 1, 0, 0, 0, 0],
       [0, 0, 1, 1, 1, 0, 0, 0],
       [0, 1, 1, 0, 1, 1, 0, 0],
       [1, 1, 0, 0, 0, 1, 1, 0],
       [1, 1, 1, 1, 1, 1, 1, 0],
       [1, 1, 0, 0, 0, 1, 1, 0],
       [1, 1, 0, 0, 0, 1, 1, 0],
       [0, 0, 0, 0, 0, 0, 0, 0]], dtype=uint8)


the reverse, np.packbits, also is available; from a boolean or uint8 array
[Y][X], you must first rotate 270 degrees (== [X][Y]) before packing.

>>> repacked = np.packbits (np.rot90 (unpacked,3), -1).reshape (8)
>>> repacked
memmap([120, 124,  22,  19,  22, 124, 120,   0], dtype=uint8)

>>> (repacked == fnt[testchar]).all()
True

>>> menus_dtype = np.dtype (dtypes['menus.bin'])#menus_dtype)
>>> menus_dtype.itemsize
46

>>> menus = mmap ('menus.bin', menus_dtype)
>>> yamlok (dump_memmap (menus))
True

>>> singlepal_dtype = np.dtype (dtypes['pal'])
>>> npals = os.path.getsize ('viking.pal') / 16
>>> npals -= 1
>>> oldpal_dtype = [BLOAD_HEADER, ('palettes', (singlepal_dtype, npals))]
>>> pal_dtype = [('header', singlepal_dtype), ('palettes', (singlepal_dtype, npals))]
>>> pal = mmap ('viking.pal', pal_dtype)
>>> yamlok (dump_memmap (pal))
True

>>> pal[0]['palettes'][:2]
array([[  0,   8,   2,   3,   4,   5,   6,  75,   7,   9,  10,  11,  12,
         13,  14,  15],
       [105, 241, 255, 252, 249, 246, 243,  58,  55,  52,  49, 153, 150,
        147, 145,  90]], dtype=uint8)

>>> map_dtype = dtypes['map'] 

>>> adjust_for_binsize (map_dtype, binsizes[0]['map'])
>>> np.dtype (map_dtype).itemsize
50
>>> map = mmap ('viking.map', map_dtype)
>>> yamlok (dump_memmap (map))
True

>>> menuitem_dtype = dtypes ['menuitem.bin']

>>> menuitem = mmap ('menuitem.bin', menuitem_dtype)
>>> menuitem[0]
(1, (5, 'Items'), 0, 1, 0, 0, 0, 0, 0, [0, 0], [0, 0, 0])

>>> enemy_dtype = dtypes['dt1']

>>> enemy_dtype = np.dtype (enemy_dtype)
>>> enemy_dtype.itemsize
320

>>> offset = 0
>>> for name in enemy_dtype.names:
...     print '@%03d %s %d' % (offset/2, name, enemy_dtype[name].itemsize)
...     offset += enemy_dtype[name].itemsize
@000 name 34
@017 thievability 2
@018 stealable_item 2
@019 stealchance 2
@020 raresteal_item 2
@021 raresteal_chance 2
@022 dissolve 2
@023 dissolvespeed 2
@024 deathsound 2
@025 unused 56
@053 picture 2
@054 palette 2
@055 picsize 2
@056 rewards 12
@062 stats 24
@074 bitsets 10
@079 spawning 26
@092 attacks 46
@115 unused2 90

Awesome! I just realized how useful the above snippet is! Since it shows all
offsets, it's easy to see where the wiki data spec deviates from the actual 
data format.


>>> enemy = mmap ('viking.dt1', enemy_dtype)
>>> enemy[1]
((6, 'D\x00a\x00m\x00n\x00e\x00d'), 0, 0, 0, 0, 0, 0, 0, 0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0, 0, 0, (5, 5, 0, 0, 0, 0), (10, 0, 5, 5, 0, 5, 0, 0, 5, 0, 0, 0), [0, 0, 0, 64, 0, 0, 0, 0, 0, 0], (0, 0, 0, 0, [0, 0, 0, 0, 0, 0, 0, 0], 0), ([1, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]), [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

>>> yamlok (dump_memmap (enemy))
True

------------------------------------
Schizophrenics such as 'attack data'
------------------------------------

This is the type of the combined array that dt6 and attack.bin create:

>>> attack_dtype = dtypes['_attack']

This is just the dtype of the parts that are in dt6

>>> dt6_dtype = dtypes['dt6']

By the way, never use a mode 'rw+' with np.memmap: it causes a segmentation fault
on NumPy v1.2 (and doesn't make sense anyway :)

>>> dt6 = np.memmap ('viking.dt6', dtype = dt6_dtype, mode = 'r+')
>>> yamlok (dump_memmap(dt6[0]))
True

apparently, VIKINGS doesn't use many captions, so I'll search for one.

>>> index = 0
>>> for i,entry in enumerate (dt6):
...     if entry['captionpt1']['length'] > 0:
...         index = i; break

>>> index
1

Irony.

Now I'll adjust the name so it's more printable.

>>> fix_stringjunk (dt6, ['name'], doubled = True)

>>> dt6[index]
(12, 60, 0, 1, 0, 3, 3, 5, (0, 0, 0), 0, 0, 0, 1, 0, 0, 1, 0, 0, [1, 16, 0, 0, 0, 0, 2, 40], (7, 0, 'R.e.c.o.v.e.r'), 0, (16, 'Reco'))

>>> np.asarray(dt6[index]).tolist()

YAML generation is not that hard (double-escape embedded weird characters in strings,
control indentation level, translate weird string encodings, 
and decide whether to represent subarrays in block or linear form), 
but it is recursive, which makes my head spin sometimes.

So I was curious what numpy save() would make of it.

>>> from cStringIO import StringIO
>>> out = StringIO()
>>> np.save (out, dt6[index])
>>> len (out.getvalue())
768

The format above is safe for inter-machine transport, and is self-describing..
which is to say, I can np.load() it and get an identical array without providing
any further data or doing any tweaking.

The reason it is so relatively large is its self-describing nature. 
All field names and their types must be recorded once.
(so it's smart to use multiple-record arrays when size matters (usually
when the number of records is high and the record size is low))

Here, the dtype description and structure far outweighs the actual
content (80 bytes of content versus 688 bytes of everything-else;
that is, the size has been increased to 9.5x of content size.)

>>> instr = StringIO (out.getvalue())
>>> loaded_dt6_item = np.load (instr)
>>> loaded_dt6_item
array((12, 60, 0, 1, 0, 3, 3, 5, (0, 0, 0), 0, 0, 0, 1, 0, 0, 1, 0, 0, [1, 16, 0, 0, 0, 0, 2, 40], (7, 0, 'R.e.c.o.v.e.r'), 0, (16, 'Reco')), 
      dtype=[('picture', '<i2'), ('palette', '<i2'), ('animpattern', '<i2'), ('targetclass', '<i2'), ('targetsetting', '<i2'), ('damage_eq', '<i2'), ('aim_math', '<i2'), ('baseatk_stat', '<i2'), ('cost', [('hp', '<i2'), ('mp', '<i2'), ('money', '<i2')]), ('xdamage', '<i2'), ('chainto', '<i2'), ('chain_percent', '<i2'), ('attacker_anim', '<i2'), ('attack_anim', '<i2'), ('attack_delay', '<i2'), ('nhits', '<i2'), ('target_stat', '<i2'), ('preftarget', '<i2'), ('bitsets1', '|u1', 8), ('name', [('length', '<i2'), ('unused', '<i2'), ('value', '|S20')]), ('captiontime', '<i2'), ('captionpt1', [('length', '<i2'), ('value', '|S4')])])

The reason that looks different is because it's not a memory-mapped
array, just an ordinary array.

however we can still use it to write back, since it's content is in
the exact same format:

>>> dt6[index] = loaded_dt6_item

and, if you view dt6[index] as a normal array,
you can see that it is actually identical.

>>> np.asarray (dt6[index])
array((12, 60, 0, 1, 0, 3, 3, 5, (0, 0, 0), 0, 0, 0, 1, 0, 0, 1, 0, 0, [1, 16, 0, 0, 0, 0, 2, 40], (7, 0, 'R.e.c.o.v.e.r'), 0, (16, 'Reco')), 
      dtype=[('picture', '<i2'), ('palette', '<i2'), ('animpattern', '<i2'), ('targetclass', '<i2'), ('targetsetting', '<i2'), ('damage_eq', '<i2'), ('aim_math', '<i2'), ('baseatk_stat', '<i2'), ('cost', [('hp', '<i2'), ('mp', '<i2'), ('money', '<i2')]), ('xdamage', '<i2'), ('chainto', '<i2'), ('chain_percent', '<i2'), ('attacker_anim', '<i2'), ('attack_anim', '<i2'), ('attack_delay', '<i2'), ('nhits', '<i2'), ('target_stat', '<i2'), ('preftarget', '<i2'), ('bitsets1', '|u1', 8), ('name', [('length', '<i2'), ('unused', '<i2'), ('value', '|S20')]), ('captiontime', '<i2'), ('captionpt1', [('length', '<i2'), ('value', '|S4')])])

I'll also show, if you're not familiar with numpy, how to get and save a number of records
as one big array.

>>> somedt6s = dt6[index:index+16]

We just grabbed 16 consecutive records from dt6:

>>> len(somedt6s)
16

That's 16*80 = 1280 bytes of content + 688  of structure, right?
that would be 1.5x inflation (1280 + 688 = 1968)

>>> outfile = os.path.join (tmpdir, 'some16.dt6.npy')
>>> np.save(outfile, somedt6s)
>>> os.path.getsize (outfile)
1968L

NumPy indexing can be quite fancy, though.
aside from the normal extended-slice notation
where you can grab a contiguous range or a stepped range::

 (':16' = first 16 items (0..15), 
  ':16:2' = every second record up to #16 (== 8 items),
  ':-2' = every record except the last two
  '4:16:3' == every third record between #4 and #16 (ie 4,7,10,13)),

you can grab literally any collection of records.
Here, I'll stick together records 1, 5, 9, 2, 32 and 42, in that order.

>>> indices = (1, 5, 9, 2, 32, 42)

>>> otherdt6s = dt6.take (indices)
>>> len (otherdt6s) == len(indices)
True

>>> for thisindex, record in zip (indices, otherdt6s):
...     print (dt6[thisindex] == record).all()
True
True
True
True
True
True


This is the dtype of the part in attack.bin

>>> attack_bin_dtype = dtypes['attack.bin']

>>> attack_bin_dtype = np.dtype (attack_bin_dtype)
>>> attack_bin_dtype.itemsize
122

>>> attack_bin = mmap ('attack.bin', attack_bin_dtype)
>>> attack_bin[index]
('vers 100 HPs', 0, 0, 0, 0, 0, 0, 0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], (0, ''), [0, 0, 0], [0, 0, 0], 8, 0)

A mechanism where I can appear to do memmapped writing to dt6 and attack.bin based on the
combined array is best.

Watch this space.



Misc thoughts
-----------------


There are several array data types. For quick, lazy I/O, memmap is the one of choice.
However, there is a type 'recarray' which provides nice attribute access to its fields.
That is, rather than typing foo[200]['name'], you can do
foo.name[200] (and this is also the caveat, you must put the indexing at the end
rather than start -- it's invalid to type foo[200].name)

If you have a normal array, you can get a recarray view on it like this::
  r = arr.view (np.recarray)

In case you are not familiar with NumPy conventions, a view is essentially the
same data viewed in a different way. It refers to the same memory area, 
which means that any changes made to the view will appear in the original.
It's important to remember to copy data if, say, you grab a record and 
just want to scratch around on it a bit. in that case you should copy it first::
  c = arr.copy()

So that, for instance, when you take a slice of our memmapped dt6 above, you needn't
fear accidentally overwriting the on-disk data.

One thing that is missing is a unifying access point.
Like::
  l = lumpHandler ('vikings.rpgdir')
  dt6 = l['dt6']


Here's a simple way to make a collection of items::
  mapping = {'attack.bin':someattacks, '.pt6':someattackgfx}
  numpy.savez ('/tmp/collection.npz', **mapping)
  
It could be improved by autodetecting zipped filename from array dtype.

And if we wanted to attach an index, we could use 
a very simple YAML format (simple enough to parse with a single regexp)::

  index = """.pt6 : [0, 1, 2, 3]
  attack.bin : [0, 1, 3, 8]"""
  import zipfile as zf
  z = zf.ZipFile ('/tmp/collection.npz','a')
  z.writestr ('INDEX', index)
  z.close()

The addition of that index saying "records 0,1,2,3 of pt6 and 0, 1, 3, 8 of
attack.bin are included" turns it into a simple patch format, which you could 
apply like this::
  import yaml
  data = np.loadz ('/tmp/collection.npz')
  rawindex = data['INDEX']
  index = yaml.safe_load (rawindex)
  for name, indices in index.items():
      dest = l[name]
      for i,v in zip(indices, data[name]):
          dest[i] = v

For an easy way of debugging fonts and other graphics, 
matplotlib is handy if you have it::

  from pylab import show, imshow, gray, jet
  def qvu (image):
      imshow (image, interpolation = 'nearest')
      show()
  # set the colormapping to gray.
  # for non-binary images (eg sprites), jet() is better.
  # you can also construct your own colormap, or simply provide
  # a color image (shaped (h, w, 3) or (h, w, 4)) to start with; 
  # this is left as an exercise for the reader.
  gray()
  character = unpack_character (fnt[ord('A')])
  qvu (character)

Incorporates zooming, panning etc. Of course matplotlib is incredibly powerful 
and can do a lot more than this, 
eg:
* it can have multiple subplots, so you can compare images 
  with individual zooming + panning. 
* It has primitive interactive facilities, so you can make buttons to 
  rotate a sprite 90deg, flip, etc.. any transform you could do without major
  user input using NumPy.
* You can plot two records (say, heros) in two subplots as (1, N) or (N, N)
  images, and plot an image showing the difference in a third subplot.
  You might list the changed fields as an xlabel for the third plot.


List of unimplemented formats
-----------------------------

(also including formats which aren't finished)

  LOOKUP.BIN  
  BAM . Map Format . HSP
  HSZ . (Combining attack data)

The following formats are obsolete, and not implemented due to that fact:

  DOR SNG

Caveats
--------------------
Embedded nulls in strings are possible but quite awkward to handle.
I'm pretty sure nobody actually uses them though.



List of formats that I plan to implement last or not at all
-----------------------------------------------------------

  BAM . HSP . HSZ

IMO none of these have particular relevance from a 'data debugging' point of view.

List of implemented formats
-----------------------------

* ATTACK.BIN
* ARCHINYM.LMP
* BROWSE.TXT
* DEFPAL?.BIN
* FIXBITS.BIN
* MENUITEM.BIN
* MENUS.BIN
* PALETTES.BIN
* SFXDATA.BIN
* SONGDATA.BIN
* UICOLORS.BIN
* DT0
* DT1
* DT6
* EFS
* FNT
* FOR
* GEN
* ITM
* MAS
* MXS
* PAL
* PT?
* SAY
* SHO
* STF
* TAP
* TMN
* VEH
* Map Formats
** N??
** L??
** D??
** E??
** P??
** T??
** MAP 
** MN
>>> logfile.close()



Silliness - translating OHRRPGCE lump format -> HDF5
-----------------------------------------------------

I'm doing this for a similar reason, to familiarize myself with HDF5 workings.

If you don't have PyTables installed, ignore the errors which will be
generated by the following code.

One easy format is PAL, 16-color palettes.
We will assume that ``pal`` is of the non-BLOAD type, as that is what we loaded
above.

>>> import tables as t
>>> filename = os.path.join (tmpdir, 'vikings.hdf5')
>>> pal[0]['palettes'].shape
(177, 16)

>>> shape = pal[0]['palettes'].shape[:-1]

Open with compression, so a reasonable resulting filesize occurs.

>>> filters = t.Filters (complevel = 5, complib = 'zlib')
>>> h5f = t.openFile (filename, 'w', filters = filters)
>>> atom = t.UInt8Atom (shape = (16,))
>>> ary = h5f.createEArray (h5f.root, 'pal16', atom, (0,), title = '16 color palettes')
>>> ary.append (pal[0]['palettes'])

ary[:] = pal[0]['palettes'][:]

>>> ary.attrs # doctest: +ELLIPSIS
/pal16._v_attrs (AttributeSet), 4 attributes:
   [CLASS := 'EARRAY',
    EXTDIM := ...,
    TITLE := '16 color palettes',
    VERSION := '1.0']

>>> ary.attrs.header = pal[0]['header'].tolist()
>>> ary.attrs.header
[92, 17, 176, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

>>> ary[100]
array([  0,  49, 241,  65, 178, 243, 245, 182,   0, 247, 184, 249,  73,
       252,  15, 249], dtype=uint8)

>>> ary
/pal16 (EArray(177,), shuffle, zlib(5)) '16 color palettes'
  atom := UInt8Atom(shape=(16,), dflt=0)
  maindim := 0
  flavor := 'numpy'
  byteorder := 'irrelevant'
  chunkshape := (8192,)

>>> ary.append ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
>>> ary[-2:]
array([[  0,  80, 179,   8, 211, 179, 224, 195, 181, 217, 183, 203, 201,
        204, 206, 221],
       [  0,   1,   2,   3,   4,   5,   6,   7,   8,   9,  10,  11,  12,
         13,  14,  15]], dtype=uint8)

>>> ary.shape
(178,)

>>> h5f.close()








Clean up (comment this section if you want to check the results)

>>> import glob
>>> for fname in glob.glob (os.path.join (tmpdir,'*')):
...     os.remove (fname)

>>> os.rmdir (tmpdir) 
