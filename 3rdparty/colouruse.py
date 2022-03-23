#!/usr/bin/env python

# OHRRPGCE colour-use counter. v0.20
# Requires nohrio: http://gitorious.org/nohrio
# Requires pygame to do anything useful
# Public Domain.

import sys
import numpy as np
from nohrio.ohrrpgce import *
from nohrio.ohrstring import *
from nohrio.ohryaml import array2py


class RPGdir(object):
    # headers for lumps used in this script
    lumpheaders = {'gen': BLOAD_SIZE, 'palettes.bin': 2*2, 'n': BLOAD_SIZE}
    
    def __init__(self, game):
        if game[-1] != '\\' and game[-1] != '/':
            game += '/'
        self.game = game
        self.archinym = archiNym(game + 'archinym.lmp').prefix

    def lump(self, name, dtype = None, lumptype = None, **more):
        if name[0] == '.':
            filen = self.game + self.archinym + name
        else:
            filen = self.game + name
        if lumptype == None:
            lumptype = name.strip('.')
        if dtype == None:
            dtype = np.dtype(dtypes[lumptype])
        offset = 0
        if lumptype in self.lumpheaders:
            offset = self.lumpheaders[lumptype]
        return mmap(filen, dtype, offset, **more)

    def maplump(self, prefix, number):
        if number < 100:
            name = '.' + prefix + str(number).zfill(2)
        else:
            name = str(number) + '.' + prefix
        return self.lump(name, lumptype = prefix)

    def defpal(self, ptno, picture, pal):
        if pal == -1:
            # don't catch: should have lump if default needed
            return self.lump('defpal%d.bin' % ptno, lumptype = 'defpal%d.bin')[picture]['palette']
        else:
            return pal

    def picnpal(self, ptno, picture, pal):
        return picture, self.defpal(ptno, picture, pal)

def record(memmap, recno = 0):
    return array2py(memmap)[recno]

def unpackpt(array, ptshape):
    """Unpacks pixels from a .pt? memmap, returning a [frames][rows][columns] array"""
    t = np.empty((len(array), 2), np.uint8).transpose()
    t[0] = array >> 4
    t[1] = array % 16
    result = t.transpose().reshape(ptshape[2], ptshape[0], ptshape[1]).transpose(0, 2, 1)
    return result


#game = RPGdir('vikings/vikings.rpgdir')
if len(sys.argv) >= 2:
    game = RPGdir(sys.argv[1])
else:
    sys.exit("Specify path to an unlumped RPG as first argument.")
    pass

gen = game.lump('.gen')[0]

tilepixelcounts = np.zeros(256, int)
backdroppixelcounts = np.zeros(256, int)
spritepixelcounts = np.zeros(256, int)
coluse = np.zeros(256, int)


print("Counting sprite pixels")
sprpixels = [[] for i in range(9)]
sprpals = [[] for i in range(9)]
for ptno in range(9):
    try:
        lmp = game.lump('.pt%d' % ptno)
    except IOError as e:
        # Old games might not have all lumps, cool with me
        continue
    for spriteset in lmp['pixels']:
        tempcount = np.bincount(unpackpt(spriteset, ptshapes[ptno]).flat)
        tempcount.resize(16)
        # exclude background
        sprpixels[ptno].append(tempcount[1:])
    sprpals[ptno] = [set() for i in lmp]


def scanforpalettes(sprpals):
    # Now look everywhere where sprites are used and find out which palettes each
    # are used with.
    print("Scanning RPG for sprite usage")

    # NPCs: Walkabouts
    for mapno in range(gen['maxmap'] + 1):
        npcs = game.maplump('n', mapno)
        for i, npc in enumerate(npcs['npc']):
            pic, pal = game.picnpal(4, npc['picture'], npc['palette'])
            sprpals[4][pic].add(pal)

    # Heroes: Walkabouts, Hero sprites, Portraits
    for hero in game.lump('.dt0'):
        if get_str16(hero['name']):
            pic, pal = game.picnpal(0, hero['battlesprite'], hero['battlepalette'])
            sprpals[0][pic].add(pal)
            pic, pal = game.picnpal(4, hero['walksprite'], hero['walkpalette'])
            sprpals[4][pic].add(pal)
            pic = hero['portrait']
            if pic > -1:
                pal = game.defpal(8, hero['portrait'], hero['portrait_palette'])
                sprpals[8][pic].add(pal)

    # Textboxes: Fixed portraits
    for box in game.lump('.say'):
        if box['portraittype'] == 1: #fixed
            pic, pal = game.picnpal(8, box['portraitpic'], box['portraitpal'])
            sprpals[8][pic].add(pal)

    # Enemies
    for enemy in game.lump('.dt1'):
        ptno = enemy['picsize'] + 1
        pic, pal = game.picnpal(ptno, enemy['picture'], enemy['palette'])
        sprpals[ptno][pic].add(pal)

    # Attacks: currently requires spliceattack to be run on the RPG, skip if not done.
    try:
        attacks = game.lump('attack.full')
    except IOError:
        print("Warning: did not process attacks; run spliceattack on the RPG")
    else:
        for attack in attacks:
            pic, pal = game.picnpal(6, attack['picture'], attack['palette'])
            sprpals[6][pic].add(pal)

    # Box borders
    try:
        defpal7 = game.lump('defpal7.bin', lumptype = 'defpal%d.bin')
    except IOError:
        pass
    else:
        for border, pal in enumerate(defpal7['palette']):
            sprpals[7][border].add(pal)

    # Items: Weapons
    for item in game.lump('.itm'):
        if item['equippable'] == 1:  #weapon
            pic, pal = game.picnpal(5, item['weaponpic'], item['weaponpal'])
            sprpals[5][pic].add(pal)

scanforpalettes(sprpals)

######
print("Summing sprite pixels")

pal16 = game.lump('.pal')
palmaps = []
for palette in pal16:
    # exclude background (colour 0 will be counted over and over anyway)
    palmaps.append(palette['indices'][1:])
    for col in np.unique(palmaps[-1]):
        coluse[col] += 1

for ptno in range(9):
    for pic in range(len(sprpals[ptno])):
        for pal in sprpals[ptno][pic]:
            spritepixelcounts[palmaps[pal]] += sprpixels[ptno][pic]
#del pal16, palmapping, uicols
#del sprpals, sprpixels


def counttilpixels(coluse, tilepixelcounts, backdroppixelcounts):
    print("Counting tileset & backdrop pixels")
    for array, lmp in [(tilepixelcounts, game.lump('.til')), (backdroppixelcounts, game.lump('.mxs'))]:
        for tset in lmp['planes']:
            tempcount = np.bincount(tset.flat)
            tempcount.resize(256)
            array += tempcount
            coluse += tempcount.clip(0, 1)

counttilpixels(coluse, tilepixelcounts, backdroppixelcounts)

uicols = game.lump('uicolors.bin')[gen['masterpal']]

# numpy apparently has no way to select fields from a record. It's discussed
# as a potential future feature. Neither is it possible to do this, because
# the new dtype is a different length:
#uidtypehack = dict(uicols.dtype.fields)
#del uidtypehack['textboxframe']
#uicols = uicols.view(np.dtype(uidtypehack))
# therefore, a bit of a hack
for col in uicols.view((INT, uicols.dtype.itemsize//2))[:48]:
    coluse[col] += 1

totalpixelcounts = spritepixelcounts + tilepixelcounts + backdroppixelcounts

print("Finished processing")

try:
    import pygame
    import pygame.font

    pygame.init()
    screen = pygame.display.set_mode((640,320), pygame.RESIZABLE)

    masterpalette = game.lump('palettes.bin')[gen['masterpal']]['color']
    colours = [pygame.Color(*col.tolist()) for col in masterpalette]

    def loadspriteset(ptno, setno, palno = -1, master = masterpalette, palettearray = pal16):
        """Returns a list of pygame surfaces, for a 4-bit spriteset's frames. Demonstration purposes."""
        pixels = unpackpt(game.lump('.pt%d' % ptno)[setno]['pixels'], ptshapes[ptno])
        pal = master[palettearray[game.defpal(ptno, setno, palno)]['indices']]
        surfaces = []
        for frame in pixels:
            #pygame expects x and y reversed
            surfaces.append(pygame.surfarray.make_surface(frame.transpose()))
            surfaces[-1].set_palette(pal)
        return surfaces

    #a_sprite = loadspriteset(0, 2)
    
    # build a hue spectrum; the scaling is primitive
    huecounts = np.zeros(360)
    for col in range(256):
        huecounts[int(colours[col].hsva[0])] += totalpixelcounts[col]
    huecounts /= huecounts[1:].max() * 0.5
    huecounts = huecounts.clip(0, 1)

    drawopts = {'dataset':1, 'numerals':True}
    def update(**options):
        """Redraws the screen, accepts arguments to change the view mode."""
        global drawopts
        drawopts.update(options)
        values = [coluse, tilepixelcounts, backdroppixelcounts, spritepixelcounts, totalpixelcounts][drawopts['dataset'] - 1]
        if drawopts['numerals'] == False:
            # scales the 16th largest value to 0.76, anything larger heads towards 1.0
            scalar = float(np.sort(values)[240])
            #print "scalar = ", scalar
            if scalar == 0.:
                colourbars = values / float(max(values.max(), 1))
            colourbars = np.tanh(values / scalar)
            
        screen.fill((0,0,0))
        #convert to ints to prevent gaps from rounding
        xs = np.require(np.linspace(0, screen.get_width(), 17), int)
        ys = np.require(np.linspace(0, screen.get_height(), 19), int)
        font = pygame.font.Font(None, int(ys[1]))
        col = pygame.Color(0)
        for y in range(16):
            for x in range(16):
                index = x + y * 16
                hsva = list(colours[index].hsva)
                if drawopts['numerals']:
                    pygame.draw.rect(screen, colours[index], (xs[x], ys[y], xs[x+1]-xs[x], ys[y+1]-ys[y]))
                    col.hsva = ((hsva[0] + 180) % 360, 100, (10000 - hsva[2] ** 2) ** .5, 100)
                    rendered = font.render(str(values[index]), True, col, colours[index])
                    screen.blit(rendered, (xs[x+1] - rendered.get_width(), ys[y]))
                else:
                    # pygame is bad at drawing zero-width rects
                    width = int(colourbars[index] * (xs[x+1]-xs[x]))
                    if width > 0:
                        col.hsva = (0, 0, 40 - 40 * (hsva[2]/100) ** 0.2, 0)
                        pygame.draw.rect(screen, col, (xs[x], ys[y], xs[x+1]-xs[x], ys[y+1]-ys[y]))
                        pygame.draw.rect(screen, colours[index], (xs[x], ys[y], width, ys[y+1]-ys[y]))

        text = '1:Colour usage','2:Tilemap pixels','3:Backdrop pixels','4:Sprite pixels','5:All graphics pixels'
        text = '   '.join([(s, '*' + s)[i == drawopts['dataset'] - 1] for i, s in enumerate(text)])
        text += '   0:Numerals/Bars'
        rendered = font.render(text, True, (255,255,255))
        screen.blit(rendered, (0, ys[16]))

        #screen.blit(a_sprite[0], (40, 40))
        
        huespace = np.linspace(0, screen.get_width(), 361)
        for x in range(360):
            col.hsva = (x, 100, 50, 100)
            pygame.draw.rect(screen, col, (huespace[x], ys[17], huespace[1]+1, ys[1]+1))
            pygame.draw.rect(screen, (255,255,255), (huespace[x], ys[17] * huecounts[x] + ys[18] * (1 - huecounts[x]),
                                                     huespace[1]+1, ys[1]+1))
        pygame.display.flip()
        
    update()

    while 1:
        #for event in pygame.event.get():
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                update(dataset = 1)
            elif event.key == pygame.K_2:
                update(dataset = 2)
            elif event.key == pygame.K_3:
                update(dataset = 3)
            elif event.key == pygame.K_4:
                update(dataset = 4)
            elif event.key == pygame.K_5:
                update(dataset = 5)
            elif event.key == pygame.K_0:
                drawopts['numerals'] ^= True
                update()
            elif event.key == pygame.K_ESCAPE:
                break
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        elif event.type == pygame.VIDEOEXPOSE:
            update()
    pygame.quit()
        
    
except ImportError:
    print("Colour usages:", coluse)
    print("Tileset pixel counts:", tilepixelcounts)
    print("Backdrop pixel counts:", backdroppixelcounts)
    print("Sprite pixel counts:", spritepixelcounts)
    print("Total pixel counts:", totalpixelcounts)
