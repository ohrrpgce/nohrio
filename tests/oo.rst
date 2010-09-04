nohrio provides an object-oriented interface to OHRRPGCE RPG files,
modelled on PyTables' API.

NOTE : These tests will only run correctly after the vikings.rpg RPGDir is either copied or linked
       into an appropriate place.
       Under Linux, ``ln -s /absolute/path/to/vikings.rpg `` while being in the 'tests/' dir
       should achieve this.
       On Windows, you will need to copy the vikings.rpg 'folder' and paste it in the 'tests/'

Inspecting an existing RPG
===========================

You begin by opening the RPG file / dir you want, specifying one of 'r' 'w' 'rw' modes
('r' is default)

>>> from nohrio import RPG, PackedImageData, md5Array
>>> import numpy as np

>>> r = RPG ('vikings.rpgdir')

To be polite, we should check if there is a passcode.
>>> print (r.passcode.get())
<BLANKLINE>

Nope.

One of the features provided by the OO interface is MD5 summing.
(of any subset of the array.)
I added that mainly to help with this testing, really  -- you don't really want to know
what all that data looks like, only that it's the same data you were expecting.

>>> r.general.md5()
'8afd584cdd1f22caf655a9093862e4af'

You can also lookup the dtype and itemsize easily (this is a feature inherited from the
NumPy implementation of arrays)

>>> r.general.dtype # doctest:+ELLIPSIS
dtype([('maxmap', ..., ('unused', '<u2', 140)])

>>> r.general.itemsize
1000

You can access even lumps that NOHRIO doesn't understand, via direct indexing of
the RPG object.

The precedence of filename lookup is in this order:

'pt0' (verbatim)
'PREFIX.pt0' (oldstyle lumps; when len(key) <=3)

>>> pt0 = r['pt0']
>>> pt0.itemsize
1
>>> pt0.shape
(15, 5120)

Multiple lookups of the same lump are cached,
so the memmap doesn't need to be initialized each time.

(We ignore entry 0, as it contains only empty space)

>>> pt0[1].md5()
'da0c94fd56a35d3d9bb1ebdd75baf302'

>>> pt0.md5()
'0033e404563067fce053fcb4e8aa666a'


Most things accessible via an RPG are some kind of OhrData.

>>> type(pt0[1])
<class 'nohrio.rpg2.OhrData'>

X.shape[0] will typically tell you how many items (graphics, stores, etc)
are in the lump.

>>> pt0.shape
(15, 5120)


^^ 15 graphics.

As NOHRIO does understand pt0, the format is autodetected.
If you want to read it in a different format or
NOHRIO won't detect the format, you can explicitly give the format:


(reading just the raw data as a bytestring)
>>> pt0 = r.data('pt0', dtype = ('B', 32*40*8/2))
>>> type(pt0[1])
<class 'nohrio.rpg2.OhrData'>

>>> pt0[1].md5()
'da0c94fd56a35d3d9bb1ebdd75baf302'

>>> pt0[1].md5() == pt0[0].md5()
False

(notice that this is the same as the previous; viewing the same data with a different dtype
won't change the hash.)


4bit Graphics classes (PT?) have methods for unpacking and repacking data.
They should automatically be chosen, but aren't yet.

>>> tmp = pt0[1].view(type = PackedImageData)

>>> image = tmp.unpack (transpose ='xy')

By default, the dimensions are guessed according to the number of bytes per record.
Dimensions are transposed relative to the http://rpg.hamsterrepublic.com/ohrrpgce/PT0
numbers.. it gives F x X x Y, ``unpack()`` output is in the order F x Y x X.
This is in order to play nice with every other image system :)

>>> image.shape
(8, 40, 32)

>>> import sys

>>> lut = ',123456789abcdef'
>>> for y in range (40):
...     for v in image[0,y]:
...         sys.stdout.write(lut[v])
...     sys.stdout.write('\n')
...     sys.stdout.flush()
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,cccccccc,,,,,,,,,,,,,
,,,,,,,,,,c46414641cc,,,,,,,,,,,
,,,,,,,,,c68864686411c,,,,,,,,,,
,,,,,,,,c4884141686141c,,,,,,,,,
,,,,,,,,c6864259486164c,,,,,,,,,
,,,,,,,,c46625b9566166c,,,,,,,,,
,,,,,,,,c646cdeec66146c,,,,,,,,,
,,,,,,,,c164fcecf66d44c,,,,,,,,,
,,,,,,,,c14cfcecf64d44c,,,,,,,,,
,,,,,,,,,c1cddeee4e141c,,,,,,,,,
,,,,,,,,,,c1688deed11c,,,,,,,,,,
,,,,,,,,,,,c1ddeed113ccc,,,,,,,,
,,,,,,,,,,c753ffa727a552c,,,,,,,
,,,,,,,,,ca2aa7332a99b955c,,,,,,
,,,,,,,,cac59ffa5a9bb9b952c,,,,,
,,,,,,,,c79bb9955fbbbb9955c,,,,,
,,,,,,,,ccbbbb9b92fbbbb9523c,,,,
,,,,,,,ccc5bb959bb2ff995a7cc,,,,
,,,,,,c7a7c55cc59992cffa7c7c,,,,
,,,,,caaaa7c3a7a755221411373c,,,
,,,,c77aa7ccaaaaa773ccccc737c,,,
,,716de77c,c37aa7733cc3ee9aac,,,
,,7664d64c,c68f386695cdded97c,,,
,,344d4661c7743384bb92eeed53c,,,
,,cc1ede44cffafac9b995cdd53c,,,,
,,,,cccccc7aa7a7c59b99ccccc,,,,,
,,,,,,,,,cfac3c37f99993c,,,,,,,,
,,,,,,,,,ca73cccacf5957c,,,,,,,,
,,,,,,,,,c7773c,c7caa7c,,,,,,,,,
,,,,,,,,,,c7333c,cccccc,,,,,,,,,
,,,,,,,,,,c441cc,c46641c,,,,,,,,
,,,,,,,,,c41111cc688664c,,,,,,,,
,,,,,,,,,cc144ccc411146c,,,,,,,,
,,,,,,,,cccc144c,c18611c,,,,,,,,
,,,,,,,c1444c41c,c11161c,,,,,,,,
,,,,,,c14444411cc164414c,,,,,,,,
,,ccccc11444111c16886411cccccc,,
,ccccccccccccccc14664411ccccccc,
,,ccccccccccccccc144411ccccccc,,

(this is an image of Kitt standing. compare with first graphic in hero graphic set #1)

>>> from nohrio.rpg2 import pack

>>> repacked = pack (image, transpose = 'xy')
>>> repacked.shape
(8, 32, 20)

>>> repacked.view(md5Array).md5()
'da0c94fd56a35d3d9bb1ebdd75baf302'

^^^ This is the same as the md5 calculated for the original data,
so they are identical.

Packing our own graphic
-----------------------

Here is a simple graphic design:

   ####
  ##  ##
  # ## #
  # ## #
  ##  ##
   ####

(6x6)

And converted into an array, it looks like:

>>> src = np.array([[0,1,1,1,1,0],
...                 [1,1,0,0,1,1],
...                 [1,0,1,1,0,1],
...                 [1,0,1,1,0,1],
...                 [1,1,0,0,1,1],
...                 [0,1,1,1,1,0]], dtype = 'B')

>>> src.shape
(6, 6)

>>> res = pack (src, transpose = 'xy')
>>> res.shape
(6, 3)

>>> res
array([[ 1, 17, 16],
       [17,  0, 17],
       [16, 17,  1],
       [16, 17,  1],
       [17,  0, 17],
       [ 1, 17, 16]], dtype=uint8)

Sub-indexed lumpsets
---------------------

This term describes lumps like... well, most map data.
Instead of having a fixed number of lumps with that format (eg. DEFPAL??.BIN),
the amount of lumps vary between RPG files.

For these, we have an interface like this:

>>> d = r.maps[0].doorlinks

(data is lazily mapped, so the map #0 doorlinks will only be memmapped after I access them)


Saving an image to PNG (requires PIL)
--------------------------------------

Remember, all arrays can be saved using NumPy's ``save()`` or ``savez()``
and loaded by ``load()``. Use of PIL is only necessary if you want to produce an image
suitable for reading by eg GIMP.

Previously, we unpacked all 8 frames of Kitt's hero graphic set.
Now we'll save that set to png.

#>>> palette = r.palettes



Creating a new RPG
==================

If an appropriate OHRRPGCE.NEW is around, nohrio can use it to create a new RPG file/dir.

>>> RPG ('/tmp/new.rpg', mode = 'w', base = 'ohrrpgce.new', dir = True)

Here we create a RPGdir ready for writing..



...

Flush the changes to disk

>>> pt0.flush()