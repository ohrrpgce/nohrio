from collections import namedtuple
from bits import Enum, MultiRange, AttrStore, mkenum
from bits.dtype import DType
from nohrio.dtypes.common import (INT16_MAX, PalettedPic,
                                  scalararray, readstr, writestr, copyfrom)
from nohrio.iohelpers import IOHandler, Filelike

chain_info = 'h:attack: h:cond_type: h:rate: 2h:cond_value: 2B:bitsets:'


DTYPE = DType("""<h:picture: h:palette: h:animpattern:
              h:targetclass: h:targetsetting:
              h:damage_eq: h:aim_math: h:baseatk_stat: 3h:cost:
              h:xdamage: h:chainto: h:chain_percent:
              h:attacker_anim: h:attack_anim: h:attack_delay:
              h:nhits: h:target_stat:
              h:preftarget: 8B:bitsets1: 12B:name: h:captiontime:
              40B:caption: h:basedef_stat:
              h:settag: h:tagcond: h:tagcheck: h:settag2: h:tagcond2:
              h:tagcheck2: 16B:bitsets2:
              40B:description: 3h:consumeitem: 3h:nitems_consumed:
              h:soundeffect:
              h:stat_preftarget: h:chaincond_type:
              h:chaincond_value: h:chaincond_value2:
              2B:chain_bitsets: T{{{chain_info}}}:else_chain:
              T{{{chain_info}}}:instead_chain:
              h:learn_sound:
              h:transmog_to:h:transmog_hpadjust:h:transmog_statadjust:
              64f:elemental_attack_failure_threshold:
              h:weapon_picture_override:h:weapon_palette_override:
              2T{h:x:h:y:}:wpoverride_handle:
              h:attack_delay_turns:
              """.format(chain_info=chain_info)).freeze()


# Enum int int
ChainCondition = namedtuple('ChainCondition', 'type val1 val2')

AnimationType = mkenum('AnimationType',
                       ('cycle forward',
                        'cycle backward',
                        'oscillate',
                        'random'),
                       MultiRange(((0,3),)))

TargetType = mkenum('TargetType',
                    ('enemy',
                     'ally excluding dead',
                     'self',
                     'all',
                     'ally including dead',
                     'ally excluding self',
                     'revenge (last hit)',
                     'revenge (whole battle)',
                     'previous target',
                     'recorded target',
                     'dead allies (heroes only)',
                     'thankvenge (last to cure attacker)',
                     'thankvenge (whole battle)'),
                    MultiRange(((0,12),)))

TargetFocusing = mkenum('TargetFocusing',
                        ('focused',
                         'spread',
                         'optional spread',
                         'random focus',
                         'first target'),
                         MultiRange(((0,4),)))

DamageEquation = mkenum('DamageEquation',
                        ('normal: atk - def * .5',
                         'blunt: atk * .8 - def * .1',
                         'sharp: atk * 1.3 - def',
                         'pure damage',
                         'no damage',
                         'set target stat to (100 + xdam)% of max',
                         'set target stat to (100 + xdam)% of current',
                         '(100 + xdam)% of max',
                         '(100 + xdam)% of current'),
                        MultiRange(((0,8),)))

AimMath = mkenum('AimMath',
                 ('normal: aim * 4 vs dog',
                  'poor: aim * 2 vs dog',
                  'bad: aim vs dog',
                  'never misses',
                  'magic: mag vs wil * 1.25'),
                 MultiRange(((0,4),)))

AttackStat = mkenum('AttackStat',
                    ('atk',
                     'mag',
                     'hp',
                     'lost hp',
                     'random (0 to 999)',
                     '100',
                     'hp (attacker)',
                     'mp (attacker)',
                     'atk (attacker)',
                     'aim (attacker)',
                     'def (attacker)',
                     'dog (attacker)',
                     'mag (attacker)',
                     'wil (attacker)',
                     'spd (attacker)',
                     'ctr (attacker)',
                     'focus (attacker)',
                     'xhits (attacker)',
                     'previous attack',
                     'last damage to attacker',
                     'last damage to target',
                     'last cure to attacker',
                     'last cure to target',
                     'hp (target)',
                     'mp (target)',
                     'atk (target)',
                     'aim (target)',
                     'def (target)',
                     'dog (target)',
                     'mag (target)',
                     'wil (target)',
                     'spd (target)',
                     'ctr (target)',
                     'focus (target)',
                     'xhits (target)',
                     'max hp(attacker)',
                     'max mp(attacker)',
                     'max atk(attacker)',
                     'max aim(attacker)',
                     'max def(attacker)',
                     'max dog(attacker)',
                     'max mag(attacker)',
                     'max wil(attacker)',
                     'max spd(attacker)',
                     'max ctr(attacker)',
                     'max focus(attacker)',
                     'max extra hits(attacker)',
                     'max hp(target)',
                     'max mp(target)',
                     'max atk(target)',
                     'max aim(target)',
                     'max def(target)',
                     'max dog(target)',
                     'max mag(target)',
                     'max wil(target)',
                     'max spd(target)',
                     'max ctr(target)',
                     'max focus(target)',
                     'max extra hits(target)',
                     ),
                    MultiRange(((0,22),)))

AttackerAnim = mkenum('AttackerAnim',
                      ('strike',
                       'cast',
                       'dash in',
                       'spinstrike',
                       'jump',
                       'land',
                       'null',
                       'standing cast',
                       'teleport'),
                      MultiRange(((0,8),)))

AttackAnim = mkenum('AttackAnim',
                    ('normal',
                     'projectile',
                     'reverse projectile',
                     'drop',
                     'ring',
                     'wave',
                     'scatter',
                     'sequential projectile',
                     'meteor',
                     'driveby',
                     'null'),
                    MultiRange(((0,10),)))

TargetStat = mkenum('TargetStat',
                    ('hp',
                     'mp',
                     'atk',
                     'aim',
                     'def',
                     'dog',
                     'mag',
                     'wil',
                     'spd',
                     'ctr',
                     'focus',
                     'xhits',
                     'poison register',
                     'regen register',
                     'stun register',
                     'mute register'),
                    MultiRange(((0, 15),)))

PreferredTarget = mkenum('PreferredTarget',
                         ('default',
                          'first',
                          'closest',
                          'farthest',
                          'random',
                          'weakest',
                          'strongest',
                          'weakest%',
                          'strongest%'),
                         MultiRange(((0, 8),)))

CaptionTime = mkenum('CaptionTime',
                     {-1: 'do not display',
                      0: 'full duration of attack'},
                     MultiRange(((-1, INT16_MAX),)),
                     lambda self: '%d ticks' % int(self))

DefenseStat = mkenum('DefenseStat',
                     ('default',
                      'hp',
                      'mp',
                      'atk',
                      'aim',
                      'def',
                      'dog',
                      'mag',
                      'wil',
                      'spd',
                      'ctr',
                      'focus',
                      'xhits'),
                     MultiRange(((0, 15),)))

TagCondition = mkenum('TagCondition',
                      ('never',
                       'always',
                       'hit',
                       'miss',
                       'kill'),
                      MultiRange(((0, 4),)))

PrefTargStrStat = mkenum('PrefTargStrStat',
                         ('target stat',
                          'hp',
                          'mp',
                          'atk',
                          'aim',
                          'def',
                          'dog',
                          'mag',
                          'wil',
                          'spd',
                          'ctr',
                          'focus',
                          'xhits',
                          'poison register',
                          'regen register',
                          'stun register',
                          'mute register'),
                          MultiRange(((0, 16),)))

ChainConditionType = mkenum('ChainConditionType',
                            ('no special conditions',
                             'tagcheck val1 + val2',
                             'attacker stat val1 > val2',
                             'attacker stat val1 < val2',
                             'attacker stat val1% > val2%',
                             'attacker stat val1% < val2%'),
                            MultiRange(((0, 5),)))

TransmogrifyStat = mkenum('TransmogrifyStat',
                          ('keep current',
                           'restore to new max',
                           'preserve % of max',
                           'keep current, cap to new max'),
                          MultiRange(((0, 3))))

class AttackId(Enum):
    valid = range(0, INT16_MAX)
    map = {0: 'No attack'}

    def _format(self):
        return '#%d' % (int(self) - 1)


class ChainInfo(AttrStore):

    def __init__(self, attack=None, rate=100,
                 condition=None, bitsets=None,
                 source=None):
        if not source:
            if attack is None:
                raise ValueError('If source is not specified,'
                                 ' attack id must be.')
            if bitsets is None:
                bitsets = BitArray('0x0000')
            condition = condition or ChainCondition(ChainConditionType(0),
                                                    0, 0)
            self.attack = attack
            self.rate = rate
            self.condition = condition
            self.bitsets = bitsets

    def _save(self, fh):
        writeint(fh, self.attack, self.condition.type, self.rate,
                 self.condition.val1, self.condition.val2)
        fh.write(lebytesfrombitsets(self.bitsets))


# with dest << src
#     .vis = PalettedPic(.picture, .palette)
#     .name = .name as ohrstr(4, 2, 10)
#     .description = .description as ohrstr(2, 1, 38)
#     .cost = .mp hp money in .cost
#     .chain = AttrStore
#     .instead, .else_ in .chain = (
#         << rate
#         .attack = .attack
#         .condition = ChainCondition(.cond_type, *.cond_value) in .chain_instead, .chain_else
#         .bitsets = .bitsets as lebitsets)
#         in .instead, .else_
#     .to in .chain = (
#         .attack = .chainto
#         .rate = .chainrate
#         .condition = ChainCondition(.chaincond, *.chaincond_value)
#
#chain_info = 'h:attack: h:cond_type: h:rate: 2h:cond_value: 2B:bitsets:'
#

class AttackData(IOHandler,AttrStore):

    def __init__(self, source, fixbits=None):
        with Filelike(source, 'rb') as fh:
            src = scalararray(DTYPE, fh.read(DTYPE.itemsize))
            self.vis = PalettedPic(src['picture'], src['palette'])
            self.name = readstr(src['name'], 4, 2, 10)
            self.description = readstr(src['description'], 2, 1, 38)
            self.cost = AttrStore()
            copyfrom(src['cost'], self.cost,
                     skeys=True, dattrs=('mp', 'hp', 'money'))
            self.chain = AttrStore()
            self.chain.to = AttrStore()
            self.chain.instead = AttrStore()
            self.chain.else_ = AttrStore()
            # change elemental interpretation according to
            #     fixbits['attack_element_fails']
            # change damage equation according to
            #     fixbits['percentage_attacks'] -- when it gets around to existing.

    def _save(self, fh):
        buf = scalararray(DTYPE)

if __name__ == "__main__":
    from io import BytesIO
    content = b''
    for filename, size in zip(('viking.dt6', 'attack.bin'),(40*2, -1)):
        with Filelike('../../ohrrpgce/vikings/vikings.rpgdir/%s' % filename, 'rb') as fh:
            content += fh.read(size)
    attack = AttackData(BytesIO(content))
    print(attack)
    #t = TileAnimationPattern('../../ohrrpgce/vikings/vikings.rpgdir/viking.')
    #print(t)
