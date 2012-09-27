#coding=utf8
#

from bits import copyattr, AttrStore
from nohrio.iohelpers import Filelike, FilelikeLump, IOHandler


class Archinym(IOHandler, AttrStore):
    """Represents general information about the structure of an RPG.

    Detailed format information :
    http://rpg.hamsterrepublic.com/ohrrpgce/ARCHINYM.LMP

    :Parameters:
      prefix : None or str
          Filename prefix (<=50 characters) for flexible-named lumps
      creator : None or str
          String identifying the software that created this rpg
      source : None or str
          Rpgdir path, or open filehandle.
          If `source` is specified, the other parameters are ignored.

    :Attributes:
      prefix :
          str
      creator :
          str



    :Examples:
      To create a new archinym:

      >>> a = Archinym ('myprefix', 'TestingCreator v-0.0.3')
      >>> a.save('/tmp/archinym.lmp')

      To load from an rpgdir:

      >>> a = Archinym (source='ohrrpgce.rpgdir')
      >>> a.prefix
      'ohrrpgce'

      >>> 'OHRRPGCE Editor' in a.creator
      True

    """
    def __init__(self, prefix='ohrrpgce', creator='nohrio pre3', source=None):
        if source:
            try:
                with Filelike(source, mode = 'rb') as fh:
                    data = fh.read()
                    data = data.decode('utf8')
                    data = data.strip()
                    newlines = data.count('\n')
                    # handle any of unix, dos, mac endlines.
                    if newlines != 1 and data.count('\r') != 1:
                        raise ValueError('Malformed data (expected 2 lines in %s,'
                                         ' got %d)' % (fh.name, newlines,))
                    prefix, creator = data.splitlines()
            except ValueError:
                raise
                #pass  # empty or nonexistent file is okay.
        prefix = prefix.lower()
        self.creator = creator
        self.prefix = prefix

    def _save(self, fh):
        for item in (self.prefix, self.creator):
            fh.write(item.encode('utf8'))
            fh.write(b'\n')

    def lumpname(self, name):
        """Return the 'prefixed' version of name, if it's a variable-named lump"""
        if '.' not in name:
            return self.prefix + '.' + name
        return name


    #XXX this may not even need to be a function..
    #    just a list of attributes to copy,
    #     after calling self.__class__.load(fh).




def _load(cls, fh):
    return cls(source=fh)
Archinym._load = _load.__get__(Archinym)
