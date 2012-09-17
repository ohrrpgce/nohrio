#coding=utf8
#

from nohrio.objutil import copyattr
from nohrio.iohelpers import Filelike, FilelikeLump, IOHandler

class Archinym(IOHandler):
    """Represents general information about the structure of an RPG.

    Detailed format information : http://rpg.hamsterrepublic.com/ohrrpgce/ARCHINYM.LMP

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
    def __init__ (self, prefix = None, creator = None, source = None):
        if source:
            try:
                with FilelikeLump (source, 'archinym.lmp') as f:
                    self.load (f)
                    return
            except IOError:
                pass # empty or nonexistent file is okay.
        self.creator = creator
        self.prefix = prefix

    def _save (self, fh):
        for item in (self.prefix, self,creator):
            fh.write(item.encode('utf8'))
            fh.write(b'\n')

    def _load (fh):
        data = fh.read().decode('utf8')
        data = data.strip()
        newlines = data.count ('\n')
        if newlines != 1:
            raise ValueError('Malformed data (expected 2 lines in %s, got %d)' % (fh.name, newlines,))
        return __class__(*data.split('\n'))
    #XXX this may not even need to be a function..
    #    just a list of attributes to copy after calling self.__class__.load(fh).
    def _reloadfrom (self, fh):
        copyattr (__class__._load(fh), self, 'prefix','creator')

