"""RELOAD document handling.

To read a document, use `read()`.
To write a document, use `root.write_root()` where `root` is the root Element.

http://gilgamesh.hamsterrepublic.com/wiki/ohrrpgce/index.php/RELOAD
"""

import struct
from nohrio.lump import CorruptionError

_byte = struct.Struct('b')
_short = struct.Struct('h')
_int = struct.Struct('i')
_bigint = struct.Struct('q')
_double = struct.Struct('d')

def check_or_message (f, n, expected, exception, message):
    tmp = f.read(n)
    if type (expected) != bytes: # filtering
        tmp = expected[0](tmp)
        expected = expected[1]
    if tmp != expected:
        raise exception(message % tmp)

def read_reload_header(f):
    """Read the reload header.

    After calling this function, the current offset of `f` will match the offset of the first
    element of the RELOAD data.

    Returns
    ========

    table : list of strings
    """
    check_or_message (f, 4, b'RELD', CorruptionError,
                      'Header string %r doesn\'t look like a RELOAD header')
    check_or_message (f, 1, (ord, 1), NotImplementedError,
                      'RELOAD version %d not understood.')
    check_or_message (f, 4, (lambda v: struct.unpack('I',v)[0], 13),
                      CorruptionError,
                      'RELOAD version 01 should always have header size=13, not %r')
    string_table_pos = struct.unpack('I', f.read(4))[0]
    f.seek (string_table_pos)
    table = read_stringtable (f)
    f.seek (13)
    return table

def read_string (f):
    length = read_vli(f)
    return f.read (length)

def write_string (f, value):
    write_vli (f, len(value))
    f.write(value)

for v in 'byte short int bigint double'.split(' '):
    size = locals()['_%s' % v].size
    exec ('def read_%s (f):\n    return _%s.unpack (f.read (%d))[0]\n' % (v,v, size))
    exec ('def write_%s (f, v):\n    f.write(_%s.pack (v))\n' % (v,v))

element_reader = {
    0 : lambda v: None,
    1 : read_byte,
    2 : read_short,
    3 : read_int,
    4 : read_bigint,
    5 : read_double,
    6 : read_string,
    }

def nop (f,v):
    pass

element_writer = {
    0 : nop,
    1 : write_byte,
    2 : write_short,
    3 : write_int,
    4 : write_bigint,
    5 : write_double,
    6 : write_string,
    }

element_size = {
    0 : 0,
    1 : 1,
    2 : 2,
    3 : 4,
    4 : 8,
    5 : 8,
    6 : -1}



class strtable (list):
    __slots__ = ()
    def __getitem__ (self, i):
        try:
            return list.__getitem__(self, i)
        except IndexError:
            raise IndexError ('index %d/%d out of range; %r' % (i,len(self), self))

    def getindex (self, string):
        try:
            i = self.index(string)
        except ValueError:
            self.append(string)
            i = len(self) - 1
        return i

class Element (object):
    __slots__ = ('name','data','children')
    def __init__ (self, name, data = None, children = None):
        self.name = name
        self.data = data
        if children:
            self.children = list (children)
        else:
            self.children = []
    def __repr__ (self):
        return "%s (%r, %r, %r)" % (self.__class__.__name__, self.name, self.data, self.children)
    def __str__ (self, depth=0):
        ret = "  " * depth
        name = self.name if self.name else "''"
        if self.data is None:
            ret += name
        else:
            ret += "%s: %s" % (name, self.data)
        for ch in self.children:
            ret += "\n" + ch.__str__(depth + 1)
        return ret
    def __eq__ (self, y):
        if self.name != y.name or self.data != y.data or \
            (len(self.children) != len(y.children)):
            return False
        # assume that for nodes to be equal,
        # their children must be ordered the same too.
        # (per Mike's explanation.)
        for ch1, ch2 in zip(self.children, y.children):
            if ch1.__eq__(ch2) != True:
                return False
        return True
    def fuzzy_eq (self, y):
        """Compare this node with another (in a less strict way than normal __eq__)

        In this case, node order is disregarded:
        {a:1, a:0} and {a:0, a:1} are considered equal.
        """
        return self.__hash__() == y.__hash__ ()

    def __hash__ (self):
        children = [v.__hash__() for v in self.children]
        children.sort ()
        datahash = (self.name, self.data)
        # 5 and 5.0 have the same hash, so need to add type
        return ((self.name, type(self.data), self.data) + tuple(children)
                      ).__hash__()

    def add_child (self, child):
        self.children.append (child)
    def del_child (self, child_or_childname):
        if type(child_or_childname) == str:
            for i,ch in enumerate(tuple(self.children)):
                if ch.name == child_or_childname:
                    self.children.pop(i)
                    return
        else:
            for i, ch in enumerate(tuple(self.children)):
                if ch == child_or_childname:
                    self.children.pop(i)
                    return
    def elementinfo (self):
        "Return `elementtype`, `datasize`"
        data = self.data
        datatype = type (data)
        if data == None:
            elementtype = 0
            elementsize = 0
        elif datatype == bytes:
            elementtype = 6
            elementsize = len(data)
            elementsize += vli_size(elementsize)
        elif datatype == str:
            elementtype = 6
            data = data.encode('latin-1')
            elementsize = len(data)
            elementsize += vli_size(elementsize)
        elif datatype in (int, float):
            if datatype == float:
                elementtype = 5
            else:
                absval = abs(data)
                elementtype = 4
                if absval < 128:
                    elementtype = 1
                elif absval < 32768:
                    elementtype = 2
                elif absval < 2147483648:
                    elementtype = 3
                # XXX will silently overflow for integers too big to store in a BIGINT!
            elementsize = element_size[elementtype]
        return elementtype, elementsize
    def size (self, table):
        """Return total on-disk size of this node, including child nodes.

        """
        mysize = self.elementinfo()[1]
        headersize = 4 + vli_size (table.getindex (self.name)) + 1 + vli_size (len(self.children))
        theirsize = sum ([ch.size(table) for ch in self.children])
        return headersize + mysize + theirsize
    def write (self, f, table):
        """Write this element to `f`.
        """
        elementtype, datasize = self.elementinfo ()
        datasize = self.size (table)
        if elementtype == None:
                raise ValueError ('Couldn\'t determine the data type')
        tagnameindex = table.getindex (self.name)
        # tagname elemtype data nchildren=0 childdata=None
        totalsize = datasize - 4
        write_int (f, totalsize)
        write_vli (f, tagnameindex)
        write_byte (f, elementtype)
        element_writer [elementtype] (f, self.data)
        write_vli (f, len(self.children))
        for ch in self.children:
            ch.write (f, table)
    def write_root (self, f):
        """Write the node and all it's children, as a full RELOAD document (ie as if it were the root node).

        The canonical usage of this is upon the actual root node,
        but it can also be used to extract any subtree.
        """
        f.write(b'RELD\x01')
        f.write(struct.pack('I', 13))
        stringtable_metapos = f.tell()
        f.write(b'    ')
        table = build_stringtable (self)
        self.write(f, table)
        string_table_pos = f.tell()
        write_stringtable (f, table)
        f.seek (stringtable_metapos)
        f.write (struct.pack('I', string_table_pos))

def read_element (f, table, recurse = True):
    """Return the next Element in `f`

    Child nodes are recursively loaded, unless `recurse` == False.

    When recurse == False, the children list is filled with NCHILDREN Ellipsis'
    (which cannot be written to disk.).
    This is typically useful only for scanning a RELOAD tree for
    appropriately-named nodes at a known level.

    """
    # size name type data nchild childdata
    # int vli byte [DATA] vli [CHILDDATA]
    size = read_int (f)
    nameindex = read_vli (f)
    name = table [nameindex]
    kind = read_byte (f)
    data = element_reader[kind] (f)
    nchildren = read_vli (f)
    # totalsize, name, data, nchildren, children_offset
    children = []
    if recurse:
        while nchildren != 0:
            children.append (read_element (f, table))
            nchildren -= 1
    else:
        while nchildren != 0:
            children.append(Ellipsis)
            nchildren -= 1
    result = Element (name, data, children)
    return result
    #return size, name, data, nchildren, f.tell ()


def read_vli (f):
    v1 = ord(f.read(1))
    mul = 1
    value = v1 & 0x3f
    shift = 6
    if v1 & 0x40:
        mul = -1
    while (v1 & 0x80):
        v1 = ord(f.read(1))
        value |= (v1 & 0x7f) << shift
        shift += 7
    value *= mul
    return value

def write_vli (f, value):
    tmp = 0
    if value < 0:
        tmp |= 0x40
    value = abs (value)
    tmp |= value & 0x3f
    if value > 0x3f:
        tmp |= 0x80
    f.write(bytes([tmp]))
    shift = 6
    if value > 0x3f:
        tmp = value >> shift
        while (tmp) != 0:
            if tmp > 0x7f:
                f.write(bytes([(tmp & 0x7f)|0x80]))
            else:
                f.write(bytes([(tmp & 0x7f)]))
            shift += 7
            tmp = value >> shift

def vli_size (v):
    "Return the number of bytes a VLI-encoded integer will occupy."
    v = abs(v)
    count = 6
    bytes = 1
    while v >= (2**count):
        count += 7
        bytes += 1
    return bytes

def read_stringtable (f):
    nstrings = read_vli (f)
    if nstrings == 0:
        raise CorruptionError ('0-length string table (?)')
    results = strtable([''])
    while nstrings > 0 :
        length = read_vli(f)
        content = f.read(length).decode('ascii')
        if len(content) != length:
            raise CorruptionError ('Truncated string table')
        results.append (content)
        nstrings-= 1
    return results

def write_stringtable (f, table):
    write_vli (f, len(table) - 1)
    for s in table[1:]:
        if isinstance(s, str):
            s = s.encode('latin-1')
        write_vli (f, len(s))
        f.write (s)

def _find_names (root, names = None):
    if names == None:
        names = {root.name:1}
    else:
        names[root.name] = names.get (root.name, 0) + 1
    for child in root.children:
        if len(child.children) > 0:
            _find_names (child, names)
        else:
            names[child.name] = names.get (child.name, 0) + 1
    return names

def build_stringtable (root):
    """Recursively discover all names in the RELOAD tree and build a string table from them.

    Places most frequently used names first, for best VLI performance.
    """
    occurrences = _find_names (root)
    occurrences.pop('', None)
    table = list(occurrences.items())
    table.sort (key = lambda v: v[1], reverse = True)
    table = strtable ([''] + [k for k,v in table])
    return table

def clean_stringtable (root, table):
    """Remove unused entries from a stringtable.
    Not implemented. May not be needed.
    """
    pass

def scan_nodes (f, table):
    """Build a dictionary mapping nodes to their starting offset in the file.

    """
    # for nodes with nchildren > 0, make two entries '%s' and '%s/'.
    # the latter will be of type `dict`, the former of type `int`
    raise NotImplementedError ()

def read (f):
    table = read_reload_header(f)
    if len(table) == 0:
        raise CorruptionError('0-length string table (?)')
    return read_element (f, table)

def reload_from_dict (d, name, key = None):
    root = Element (name)
    items = list(d.items())
    if not key:
        key = lambda v:v[0]
    items.sort (key = key)
    for k,v in items:
        if type(v) in (int, float, str, type(None)):
            root.add_child (Element (k, v))
        else:
            root.add_child (reload_from_dict (v, k))
    return root

def reload_from_seq (s, name):
    """Convert nested 3-tuples -> RELOAD tree.

    tuples can represent all possible RELOAD trees, unlike normal dictionaries.
    type(s) == tuple is not required -- just a sequence type.
    """
    root = Element (name)


__all__ = ('read','Element','read_vli','write_vli', 'reload_from_dict'),
