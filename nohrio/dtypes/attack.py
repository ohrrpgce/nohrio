from collections import namedtuple
from bits import Enum, MultiRange, AttrStore
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
              h:learn_sound:""".format(chain_info=chain_info)).freeze()


# Enum int int
ChainCondition = namedtuple('ChainCondition', 'type val1 val2')


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


class AttackData(IOHandler):

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
        for chain in (self.chain.else_, self.chain.instead):
            chain.save(fh)

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
