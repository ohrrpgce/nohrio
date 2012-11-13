# new RELOAD implementation
import collections
LAZY_THRESHOLD = 1024 * 48

LazyNode = namedtuple('LazyNode', 'filehandle name size'
                      ' nchildren data_offset children_offset')
def _load(self):
    self.filehandle.seek(data_offset, 0)
    value = get_value(self.filehandle, self.size)
    if self.nchildren:

    return Node(self.name, value,

LazyNode.load = _load


class Node(tuple):
    """Single RELOAD Node, possibly with children"""

    def __new__(cls, name, value=None, children=()):
        valuetype = type(value)
        if valuetype not in {NoneType, int, float, str, bytes}:
            raise ValueError('RELOAD doesn\'t support'
                             ' nodes of type %s' % valuetype)
        if valuetype is str:
            value = value.encode('utf8')
        return tuple.__new__(cls, (name, value, children))

    def iter(self, name, value=None):
        """Return an iterator over all children with a specified name."""
        def iterator():
            for child in self.children:
                if isinstance(child, LazyNode):
                    child = child.load()
                    if child.name == name and (
                                               (value is None) or
                                               child.value == value):
                        yield child
        return iterator()

    def __getitem__(self, k):
        if type(k) == str:

        elif isinstance(k, collections.Iterable):

