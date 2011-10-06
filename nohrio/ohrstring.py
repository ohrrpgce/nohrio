# String de/mangling
# ===================
#
# Functions for setting and getting 8 and 16-bit strings
# from numpy array-ish objects.
#
# Unlike OHRRPGCE's editor, these are 'clean' -- set operations always
# wipe unused bytes.
#
# If you want to set multiple strings, create an array of the appropriate
# dtype -- ``[('length', int16 or int8), ('value', int16 or int8, maxlength)]``
# , store your values with set_*, and assign them to the target array range.
#
#
# Beware: all set_* functions will truncate the output if you provide a value
# too long to fit.


def set_str16 (dest, src): # 16bit/8bit len, 16bit chars
    assert len (src) <= (len (dest['value']) / 2)
    dest['length'] = len(src)
    dest['data'] = "".join([char + '.' for char in src] + ['\x00\x00'])

def set_str8 (dest, src): # 16 or 8bit header, 8bit chars
    assert len (src) <= len (dest['value'])
    dest['length'] = len(src)
    dest['value'] = src + '\x00'

def get_str16 (src):
    return src['data'][:src['length']*2:2]

def get_str8 (src):
    return src['value'][:src['length']]

# the format used by OHRRPGCE .SAV gold field.
# reads/writes an integer value <-> a 16bit string 9_6

def get_intstr16 (src):
    return int (get_str16(src))

def set_intstr16 (dest, src):
    set_str16 (dest, str (src))
