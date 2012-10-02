from bits import Enum
from bits.dtype import DType
from nohrio.iohelpers import IOHandler

class Thievability(Enum):
    valid = (-1,0,1)
    map = {-1: 'never',
           0: 'once only',
           1: 'infinite'}

class DissolveType(Enum):
    valid = range(0, 11)
    map = {
            0: 'Default',
            1: 'Random pixels',
            2: 'Crossfade',
            3: 'Diagonal vanish',
            4: 'Sink into ground',
            5: 'Squash',
            6: 'Melt',
            7: 'Vapourise',
            8: 'Phase out',
            9: 'Squeeze',
            10: 'Shrink',
            11: 'Flicker'
          }

DTYPE = DType("""34B:name: h:thievability: h:stealable_item: h:stealchance:
               h:raresteal_item: h:raresteal_chance: h:dissolve: h:dissolvespeed:
               h:deathsound: 2h:battlecursor: 26h:unused: h:picture: h:palette: h:picsize: 6h:rewards: 12h:stats:
               10B:bitsets:
               T{h:death:h:nonelemdeath:h:alone:h:nonelemhit:h:amount:}:spawning:
               T{5h:regular:5h:desperation:5h:alone:8h:counterelem:12h:counterstats:56h:counterelem2:}:attacks:
               56h:elemspawn2:
               64f:elemdamage:""")

#0-16 	FVSTR (1i+16i=17i) 	Name of Enemy
#17 	INT 	Thievability of Enemy:

#-1 = Is not thievable
#0 = Once only
#1 >= Infinitely thievable
#18 	INT 	Stealable item
#19 	INT 	Item Steal Chance %
#20 	INT 	Rare stealable item
#21 	INT 	Rare Item Steal Chance % (if regular steal failed)
#22 	INT 	Dissolve animation

#0=Use default in gen(genEnemyDissolve)
#1=Random pixels
#2=Crossfade
#3=Diagonal vanish
#4=Sink into ground
#5=Squash
#6=Melt
#7=Vapourise
#8=Phase out
#9=Squeeze
#10=Shrink
#11=Flicker
#23 	INT 	Dissolve animation length in ticks (0=default: Squash,Vapourise,Phase out use sprite width/5, others use sprite width/2)
#24 	INT 	Death sound effect ID + 1 (0 for default, -1 for none)
#25 	INT 	Battle targeting cursor X offset (relative to top-center)
#26 	INT 	Battle targeting cursor Y offset (relative to top-center)
#27-52 	INT (26) 	Unused
#53 	INT 	Picture
#54 	INT 	Palette, or -1 for default
#55 	INT 	Picture Size:

#0 = Small (From PT1)
#1 = Medium (From PT2)
#2 = Large (From PT3)
#56 	INT 	Gold reward
#57 	INT 	Experience reward
#58 	INT 	Item reward
#59 	INT 	Item drop %
#60 	INT 	Rare item
#61 	INT 	Rare item drop % (If a regular item is not dropped)
#62 	INT 	HP
#63 	INT 	MP
#64 	INT 	Strength
#65 	INT 	Accuracy
#66 	INT 	Defense
#67 	INT 	Dodge
#68 	INT 	Magic
#69 	INT 	Will
#70 	INT 	Speed
#71 	INT 	Counter
#72 	INT 	MP~
#73 	INT 	Extra Hits
#74-78 Enemy Bitsets 	BIT (8) 	0 - 7: Weak to Elemental 1 - 8 (Obsolete, see #Note 1)
#BIT (8) 	8 - 15: Strong to Elemental 1 - 8 (Obsolete, see #Note 1)
#BIT (8) 	16 - 23: Absorbs Elemental 1 - 8 (Obsolete, see #Note 1)
#BIT (8) 	24 - 31: Is Enemytype 1 - 8 (Obsolete, see #Note 1)
#BIT (22) 	32 - 53: Unused
#BIT 	54: Harmed by Cure
#BIT 	55: MP Idiot
#BIT 	56: Boss
#BIT 	57: Unescapable
#BIT 	58: Die Without Boss
#BIT 	59: Flee instead of Die
#BIT 	60: Untargetable by Enemies
#BIT 	61: Untargetable by Heros
#BIT 	62: Win battle even if left alive
#BIT 	63: Never flinch when hit
#BIT 	64: Ignored for "Alone" AI
#BIT (15) 	65 - 79: Unused
#79 	INT 	Enemy to Spawn on death + 1
#80 	INT 	Enemy to Spawn on Non-Elemental Death + 1
#81 	INT 	Enemy to Spawn when alone + 1
#82 	INT 	Enemy to Spawn on Non-Elemental Hit + 1
#83-90 	INT (8) 	Enemy to Spawn on Elemental 1 - 8 Hit + 1
#91 	INT 	Number of enemy copies to spawn on spawn trigger
#92-96 	INT (5) 	Regular attacks + 1, 0 if unused
#97-101 	INT (5) 	Desperation attacks + 1, 0 if unused
#102-106 	INT (5) 	Alone attacks + 1, 0 if unused
#107-114 	INT (8) 	Counter attack to elementals 1-8. atk_id + 1, 0=none
#115-126 	INT (12) 	Counter attack damage to stats. atk_id + 1, 0=none
#127-182 	INT (56) 	Counter attack to elementals 8-63. atk_id + 1, 0=none
#183-238 	INT (56) 	Enemy to Spawn on Elemental 9-64 Hit + 1
#239-366 	FLOAT (64) 	Damage taken from elemental 1-64 (1.0 is 100%) #Note 1

class Enemy(IOHandler):
    def __init__(self, source):
        pass
    def _save(self, fh):
        pass
