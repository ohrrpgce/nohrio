# Data type definitions
# =====================
#
# Mostly named according to description rather than filename

from ohrrpgce import dtypes as _dt
import numpy as np
dt = {}
for name, dtype in _dt.items():
    dt[name] = np.dtype (dtype)

# World domination
# ----------------

GENERAL = dt['gen']
BROWSE_INFO = dt['browse.txt']
RECORD_SIZES = dt['binsize.bin']

# Graphics
# --------
#
# All of the 16-color graphics lumps (GAMENAME.PT?) are headerless
# and consist entirely of packed 16color pixels,
# each record considered as (NFRAMES, HEIGHT, WIDTH/2) array of bytes.
#

HEROGFX
WALKGFX
ENEMYGFX_SMALL
ENEMYGFX_MID
ENEMYGFX_LARGE
ATTACKGFX
TEXTBOXGFX
PORTRAITGFX

DEFAULTPAL = dt['defpal%d.bin']

# 256-color graphics lumps currently number 2:
# TIL and MXS, which are both headerless and consist of 64,000 byte
# (320x200) records made up of 4 16000-pixel planes (80 x 200 pixels)
#
#
#

TILESET = np.dtype ('B', (4,80,200))
BACKGROUND = TILESET

TILESET_LINEAR = np.dtype ('B', (320, 200))
BACKGROUND_LINEAR = TILESET_LINEAR

# Fonts are a 256[8]

FONT = dt['fnt']


# Tile Animation Patterns are simply lists of instructions for a tile animation
# virtual machine.
TILE_ANIMATION = dt['tap']

# Battle
# --------
#
# see Graphics_ for dtypes relating to battle graphics

ATTACK = dt['attack.full']
HERO = dt['dt0']
ENEMY = dt['dt1']
FORMATION = dt['for']
FORMATION_SET = dt['efs']


# Map
# ----

DOORDEF
DOORLINKS
PASSABILITY_DEFAULTS = dt['defpass.bin']


# Interaction
# -------------
#
