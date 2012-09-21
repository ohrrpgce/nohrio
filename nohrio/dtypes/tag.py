#coding=utf8
"""

"""

import numpy as np
import struct
from nohrio.lru_cache import lru_cache
from nohrio.nohrio2 import INT
from bits import metadata
from nohrio.iohelpers import IOHandler, loadstruct

_FIXEDVALUES = (-1,0,1)


# Note that the following works to bind arbitrary outer names to inner (class) attributes:
#
# class F(int):
#     for v in ('foo','bar','bza'):
#         locals()[v] = 11
#
# >>> v.foo
# 11
#
# This is because a class is just a scope where you can put statements, with a few special behaviours.
#
#
# also:
# cf http://stackoverflow.com/questions/1015307/python-bind-an-unbound-method
#
# All functions are also descriptors, so you can bind them by calling their __get__ method:
#     bound_handler = handler.__get__(self, MyWidget)
# http://users.rcn.com/python/download/Descriptor.htm <- R.Hettinger's excellent guide to descriptors.
#
#
#
# Ultimately, I've decided on the following, using descriptors:
#
# def load_foo(cls, fh):
#     #do stuff
#     return newinstance
#
# class Foo(int):
#     pass
#
# Foo.load = load_foo.__get__(Foo)
#
#
dtype = np.dtype(INT)


def load (cls,fh):
    return cls(*IOHandler._load_struct(cls, fh))

class _TagCheck(int, IOHandler):
    """Base class for tag checks.

    Do not instantiate this; instead call TagCheckClass(rpg) to get a
    subclass for this specific RPG, and instantiate that class.
    """
    struct = struct.Struct(dtype.byteorder + dtype.char)
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
        params = format % self.index
        return '%s(%s)' % ( self.__class__.__name__, params)

    def __repr__ (self):
        format = 'off = %d' if int.__lt__ (self, 0) else 'on = %d'
        params = format % abs(int(self))
        return 'TagCheckClass(%r)(%s)' % (self.rpg,params)

    def _save (self, fh):
        IOHandler._save_struct(self, fh, self)

    def _index (self):
        return abs(int(self))
    index = property(_index, doc ='Return the tag # this TagCheck examines.')

    def _match(self):
        """Return what state the tag needs to be in to satisfy the check"""
        return int(self) > -1
    match = property(_match)

    #def _isfixed(self):
    #    if self.tagindex > 1:
    #        return None
    #    if int(self) == 1:
    #        return True
    #    return False
    #isfixed = property(_isfixed)

@lru_cache(maxsize=16)
def TagCheckClass(rpg):
    """Return a subclass of _TagCheck bound to rpg"""
    import weakref
    namespace = {'rpg': rpg}
    newcls = type(rpg.filename+'->TagCheck', (_TagCheck,),
                  namespace)
    loadfunc = loadstruct.__get__(newcls)
    newcls.load = loadfunc
    newcls.dtype = np.dtype(dtype, metadata = {'class':weakref.proxy(newcls)})
    return newcls


#class Test(object):
#    filename = 'test.ify'

#print (TagCheckClass(Test()))


__ALL__ = ('TagCheckClass',)
