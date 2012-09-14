#coding=utf8
#

from nohrio.iohelpers import FilenameOrHandleOpen, LumpOrHandleOpen, IOHandler

class Archinym(IOHandler):
    """Represents general information about the structure of an RPG.
    
    Parameters
    -----------
    prefix : None or str
        see Attributes_
    creator : None or str
        see Attributes_
    source : None or str
        Rpgdir path, or open filehandle.
        If `source` is specified, the other parameters are ignored.
    
    Attributes
    -----------
    prefix : str
        Filename prefix for flexible-named lumps
    creator : str
        String identifying the software that created this rpg
    
    See Also
    ---------
    http://rpg.hamsterrepublic.com/ohrrpgce/ARCHINYM.LMP
    
    Examples
    ----------
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
                with RpgdirOrHandleOpen (source, 'archinym.lmp') as f:
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
    
    def _load (self, fh):        
        data = fh.read().decode('utf8')
        data = data.strip()
        newlines = data.count ('\n')
        if newlines != 1:
            raise ValueError('Malformed data (expected 2 lines in %s, got %d)' % (fh.name, newlines,))
        self.prefix, self.creator = data.split('\n')
        return self
                
        