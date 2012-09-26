from collections import namedtuple

_statlist = 'hp mp str acc def dog mag wil spd ctr foc xhits'.split()
stats = ''.join('h:%s:' % v for v in _statlist)
statranges = ''.join('2h:%s:' % v for v in _statlist)
spelllist = '24T{h:attack:h:level:}'

PalettedPic = namedtuple('PalettedPic', 'pic pal')
StatList = namedtuple('StatList', 'hp mp str acc defe dog mag wil spd ctr foc xhits')