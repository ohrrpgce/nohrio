from bits import AttrStore
from nohrio.iohelpers import IOHandler, Filelike
from struct import unpack, pack
FIELDS = tuple ('attack stf songdata sfxdata map menus menuitem uicolors say npc dt0 dt1 itm'.split(' '))
DEFAULTS = (None, 64, None, None, 40, None, None, None, 400, 30, 636, 320, 200)

class Binsizes(IOHandler, AttrStore):
    def __init__ (self, source):
        with Filelike(source, 'rb') as fh:
            remaining = list(FIELDS)
            dict = self.__dict__
            lastread = 1
            while remaining and lastread:
                thiskey = remaining.pop(0)
                lastread = fh.read(2)
                if lastread:
                    lastread = unpack('<h', lastread)[0]
                    dict[thiskey] = lastread
            extradata = fh.read()
            self.EXTRA = ()
            if extradata:
                print ('BINSIZE.BIN: %d extra records detected!' % (len(extradata) / 2))
                self.EXTRA = list(unpack('<%dh' % (len(extradata) / 2), extradata))
            if remaining:
                print ('filling in defaults for (%s)' % (' '.join(remaining)))
                for k,v in zip(remaining, DEFAULTS[len(remaining):]):
                    dict[k] = v

    def _save (self, fh):
        items = [self.__dict__[k] for k in FIELDS]
        fh.write(pack('<%dh' % len(FIELDS), *items))
        if self.EXTRA:
            fh.write(pack('<%dh' % len(self.EXTRA), *self.EXTRA))

    def check (self):
        for k in FIELDS:
            if getattr(self, k) < 1:
                raise ValueError()

def _load(cls,fh):
    cls(fh)

Binsizes._load = _load.__get__(Binsizes)

#b = Binsizes('../../ohrrpgce/vikings/vikings.rpgdir/binsize.bin')
#print(b)
#b.save('/tmp/binsize.bin')
#import os
#os.system('diff ../../ohrrpgce/vikings/vikings.rpgdir/binsize.bin /tmp/binsize.bin')