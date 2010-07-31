import struct

def check_or_message (f, n, expected, exception, message):
    tmp = f.read(n)
    if type (expected) != str: # filtering
        tmp = expected[0](tmp)
        expected = expected[1]
    if tmp != expected:
        raise exception(message % tmp)

def read_reload_header(f):
    check_or_message (f, 4, 'RELD', ValueError, 'Header string %r doesn\'t look like a RELOAD header')
    check_or_message (f, 1, (ord, 1), NotImplemented, 'RELOAD version %r not understood.')
    check_or_message (f, 4, (lambda v: struct.unpack('I',v), 13), ValueError, 'RELOAD version 01 should always have header size=13, not %s')
    string_table_pos = struct.unpack('I', f.read(4))

def read_element (f):
    """Return the next element's data [non-recursively]
    """
    # size name type data nchild childdata
    # int vli byte [DATA] vli [CHILDDATA]

def read_vli (f):
    v1 = struct.unpack('B', f.read(1))
    mul = 1
    value = v1 & 0x3f
    shift = 6
    if v1 & 0x40:
        mul = -1
    while (v1 & 0x80):
        v1 = struct.unpack('B', f.read(1))
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
    f.write(struct.pack('B', tmp))
    shift = 6
    if value > 0x3f:
        tmp = value << shift
        while (tmp) != 0:
            if tmp > 0x7f:
                f.write (struct.pack('B', (tmp & 0x7f)|0x80))
            else:
                f.write (struct.pack('B', (tmp & 0x7f)|0x80))
            shift += 7
            tmp = value << shift

def write_reload_header (f, document):
    f.write('RELD\x01')
    f.write(struct.pack('I', 13))
    raise NotImplemented ('string table handling not yet implemented')
