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
'2152290934ff0aa77baac8caf9457ab2'

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
<class 'nohrio.wrappers.OhrData'>

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
<class 'nohrio.wrappers.OhrData'>

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
>>> d.md5()
'680480359d22990aeea8634d800fe370'

>>> d[:18] #doctest:+NORMALIZE_WHITESPACE
DoorLinks([[  0,  26,   1,   0,   0],
       [  3,   2,   3,   0,   0],
       [  5,   4,   3,   0,   0],
       [  7,   6,   3,   0,   0],
       [  9,   8,   3,   0,   0],
       [ 11,  10,   3,   0,   0],
       [ 13,   1,   4, -15,   0],
       [ 14,   1,   4, -15,   0],
       [ 13,   1,   5,  15,   0],
       [ 14,   1,   5,  15,   0],
       [ 16,   2,  33,   0,   0],
       [ 18,   2,   8,   0,   0],
       [ 20,   2,  18,   0,   0],
       [  0,  26,   1,   0,   0],
       [ 21,   1,   1,   0,   0],
       [ -1,   0,   0,   0,   0],
       [ -1,   0,   0,   0,   0],
       [ -1,   0,   0,   0,   0]], dtype=int16)

(data is lazily mapped, so the map #0 doorlinks
are only memmapped after I access them)

As you can see, there are only 15 door links used, out of the maximum 200,
on map #0.

>>> d = r.maps[0].doors
>>> d.md5()
'4172386cc7a3fe4b949a98cae9509af5'

>>> d[:4] #doctest:+NORMALIZE_WHITESPACE
DoorDefs([[20, 31,  1],
       [20, 33,  1],
       [38, 27,  1],
       [38, 26,  1]], dtype=int16)


As you can see, it says [20, 31, 1] for the first door.
Opening Custom, it is indeed the case that at 20,31 on map 0, there is a door
(if there wasn't, the last number would be 0, indicating an unused slot.)

Don't do this to check if a door is used:

>>> d[0].bitsets == 1
DoorDefs(True, dtype=bool)


That generally is not what you want.
Rather, do this:

>>> d.bitsets[0] == 1
True



Counting the doors used:

Because only the first bitset in the bitset field
is ever used, we can get a count of used doors via simply:

>>> d.bitsets.sum()
22



Saving an image to PNG (requires PIL)
--------------------------------------

Remember, all arrays can be saved using NumPy's ``save()`` or ``savez()``
and loaded by ``load()``. Use of PIL is only necessary if you want to produce an image
suitable for reading by eg GIMP.

Previously, we unpacked all 8 frames of Kitt's hero graphic set.
Now we'll save that set to png.

#>>> palette = r.palettes


Unlumping from an RPG file
===========================

Please note: before unlumping from a RPGFile, you should first check whether the user
can provide the correct password, if applicable.

This set of tests requires you to place a copy of or symlink to, testgame/test.rpg from the
OHRRPGCE repository, into the tests/ directory.

>>> r = RPG ('test.rpg')
>>> gen = r.unlump ('test.gen')
>>> gen # doctest:+ELLIPSIS
'...test.gen'

GEN lumps are always 1007 bytes (7 bload header, 1000 data)

>>> import os
>>> os.path.getsize (gen)
1007L

(the above test may fail if you are running too old (<2.6) version of Python.
nohrio may still work under older versions of Python, but I make no guarantees - I'm focusing
on supporting 2.6+ (and 3.x when possible))



Creating a new RPG
==================

We can create new RPG files/dirs even without any OHRRPGCE.NEW around.
We have to tell it where to write to, and what prefix to use
(Yes, it's possible to have rpg files with prefix != filename base.
Don't do that, it's evil. Perhaps I'll remove that possibility later.)

>>> from nohrio.rpg2 import create
>>> pathtorpg = create ('/tmp/test.rpg','test')
>>> rpg = RPG (pathtorpg, mode = 'r')
>>> rpg.manifest

Here we create a RPGdir ready for writing..



...

Flush the changes to disk

>>> pt0.flush()

>>> import os
>>> os.remove ('/tmp/test.rpg')
