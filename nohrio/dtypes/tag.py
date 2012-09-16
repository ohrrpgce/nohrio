#coding=utf8
import numpy as np
import struct
from bits.dtype import DType, limited, enum, bitsets, OFFSET
from nohrio.lru_cache import lru_cache
from nohrio.nohrio2 import INT
from nohrio.iohelpers import IOHandler

_FIXEDVALUES = (-1,0,1)

@lru_cache(maxsize = 16)
def _TagCheck (_rpg):
    """Return an int subclass corresponding to 'tag equipped to <rpg>'

    Parameters
    -----------
    value : int, optional
    off : int, optional
    on : int, optional
        Exactly one of these must be specified.

    """
    # I was using functools.total_ordering here, but note it doesn't work
    # when a superclass implements the other comparison operators.
    class TagCheck(int, IOHandler):
        rpg = _rpg
        dtype = np.dtype(INT)
        _struct = struct.Struct(dtype.byteorder + dtype.char)
        def __new__ (cls, value = None, off = None, on = None):
            if sum(v != None for v in (value, off, on)) != True:
                raise ValueError("Exactly one of (value,isoff,ison) must be specified.")
            if off != None:
                if off < 0:
                   raise ValueError('off must specify a positive tag index, not %d' % off)
                value = -off
            elif on != None:
                if on < 0:
                    raise ValueError('on must specify a positive tag index, not %d' % on)
                value = on
            return int.__new__ (cls, value)

        def __eq__ (self, y):
            try:
                return (self.rpg == y.rpg and int.__eq__(self, y))
            except AttributeError as e:
                pass
            return False
        __ne__ = lambda self,y: not self.__eq__(y)

        def __lt__(self, y):
            raise TypeError("Unorderable types: %s() vs %s()" % (self.__class__, y.__class__))
        __gt__ = __lt__
        __ge__ = __lt__
        __le__ = __lt__

        def __bool__(self):
            return int(self) > -1

        # XXX include tag name
        def __str__ (self):
            format = 'off = %d' if int.__lt__ (self, 0) else 'on = %d'
            if int.__eq__ (self, 0) or int.__eq__(self, -1):
                format += ' (Never)'
            elif int.__eq__(self, 1):
                format += ' (Always)'
            # else:
            #     try:
            #         format += '(%s)' % rpg.names.tag[self.tagindex()-2]
            #     except KeyError:
            #         format += '()'
            params = format % self.tagindex()
            return '%s->%s(%s)' % ( self.rpg, self.__class__.__name__, params)

        def __repr__ (self):
            format = 'off = %d' if int.__lt__ (self, 0) else 'on = %d'
            params = format % abs(int(self))
            return '%s(%r, %s)' % (self.__class__.__name__, self.rpg, params)

        def _save (self, fh):
            IOHandler._save_struct(self, fh, self)

        def _load (self, fh):
            return TagCheck(IOHandler._load_struct(self, fh)[0])
        # XXX copypasta
        load = lambda self, *args, **kwargs: IOHandler.load(self or __class__,
                                                           *args,
                                                           **kwargs)

        def tagindex (self):
            """Return the tag index this TagCheck examines"""
            return abs(int(self))
    return TagCheck

# XXX make it more obvious how to get a bound TagCheck class directly for a given rpg.
def TagCheck(rpg, value = None, off = None, on = None):
    "Class factory - returns a TagCheck class bound to `rpg`"
    cls = _TagCheck (rpg)
    return cls(value, off, on)

__ALL__ = ('TagCheck',)
