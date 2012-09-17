#coding=utf8
"""Utility functions for generic object manipulation.

"""

def metadata (**kwargs):
    """Return kwargs.

    This is a dtype annotation utility function.

    :Examples:
        >>> dt = np.dtype('h', metadata = metadata(range=(-16000,16000)))
        >>> dt.metadata['range']
        (-16000, 16000)
    """
    return kwargs

def copyattr (src, dest, *attrs):
    """Copy attribute values from src to dest

    Used to simplify IOHandler._reloadfrom/IOHandler._load methods.
    """
    for attr in attrs:
        setattr(dest, attr, getattr(src, attr))

class AttrStore(object):
    def __init__ (self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__ (self):
        return '%s(%s)' % (self.__class__.__name__, ", ".join(('%s=%r' % (k,v) for k,v in self.__dict__.items())))
    def __str__ (self):
        return self.__repr__()