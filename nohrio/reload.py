import struct

_byte = struct.Struct('b')
_short = struct.Struct('h')
_int = struct.Struct('i')
_bigint = struct.Struct('q')
_double = struct.Struct('d')

def check_or_message (f, n, expected, exception, message):
    tmp = f.read(n)
    if type (expected) != str: # filtering
        tmp = expected[0](tmp)
        expected = expected[1]
    if tmp != expected:
        raise exception(message % tmp)

def read_reload_header(f):
    """Read the reload header.

    After calling this function, the current offset of f will match the offset of the first
    element of the RELOAD data.

    Returns
    ========

    table : list of strings
    """
    check_or_message (f, 4, 'RELD', ValueError, 'Header string %r doesn\'t look like a RELOAD header')
    check_or_message (f, 1, (ord, 1), NotImplemented, 'RELOAD version %r not understood.')
    check_or_message (f, 4, (lambda v: struct.unpack('I',v), 13), ValueError, 'RELOAD version 01 should always have header size=13, not %s')
    string_table_pos = struct.unpack('I', f.read(4))
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

element_writer = {
    0 : lambda v: None,
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


def read_element (f, table):
    """Return the next element's data [non-recursively]

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
    return size, name, data, nchildren, f.tell ()

def write_element (f, table, name, data):
    """Write an element's data (element type is autodetected).

    Children nodes are currently unsupported.
    """
    #decide what element type to use
    elementtype = None
    datatype = type (data)
    if data == None:
        elementtype = 0
        datasize = 0
    elif datatype == str:
        datasize = len(str)
        elementtype = 6
    elif datatype in (int, long, float):
        if datatype == float:
            elementtype = 5
        else:
            absval = abs (data)
            elementtype = 4
            if absval < 128:
                elementtype = 1
            elif absval < 32768:
                elementtype = 2
            elif absval < 2147483648:
                elementtype = 3
        datasize = element_size[elementtype]
    if elementtype == None:
        raise ValueError ('Couldn\'t determine the data type')
    tagnameindex = None
    if name not in table:
        table.append (name)
        tagnameindex = len(table)
    else:
        tagnameindex = table.index(name)
    # tagname elemtype data nchildren=0 childdata=None
    totalsize = vli_size (tagnameindex) + 1 + datasize + vli_size(0) + 0
    write_int (f, totalsize)
    write_vli (f, tagnameindex)
    write_byte (f, elementtype)
    element_writer [elementtype](f,data)
    write_vli (f, 0)

def read_vli (f):
    v1 = ord(f.read(1))
    #print ('v1 %02x' % v1)
    mul = 1
    value = v1 & 0x3f
    shift = 6
    if v1 & 0x40:
        mul = -1
    while (v1 & 0x80):
        v1 = ord(f.read(1))
        #print ('v1 %02x' % v1)
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
    f.write (chr (tmp))
    shift = 6
    if value > 0x3f:
        tmp = value >> shift
        print ('->%d' % tmp)
        while (tmp) != 0:
            if tmp > 0x7f:
                f.write (chr ((tmp & 0x7f)|0x80))
            else:
                f.write (chr ((tmp & 0x7f)))
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

def write_reload_header (f, document):
    f.write('RELD\x01')
    f.write(struct.pack('I', 13))
    raise NotImplemented ('string table handling not yet implemented')

def read_stringtable (f):
    nstrings = read_vli (f)
    results = []
    while nstrings > 0 :
        length = read_vli(f)
        content = f.read(length)
        if len(content) != length:
            raise ValueError ('Truncated string table')
        nstrings-= 1
    return results

def write_stringtable (f, table):
    write_vli (f, len (table))
    for s in table:
        write_vli (len(s))
        f.write (s)


