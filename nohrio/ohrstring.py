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


import numpy as np

def set_str16 (dest, src): # 16bit/8bit len, 16bit chars
    assert len (src) <= (dest.dtype['data'].itemsize / 2)
    textlen = dest.dtype['data'].itemsize
    if len(dest.dtype) == 2:
        nicetype = np.dtype ([('length', np.uint16),('data', (np.uint8, textlen))])
    else:
        nicetype = np.dtype ([('length', np.uint16),('unused', np.int16),('data', (np.uint8, textlen))])
    #print dest.dtype, nicetype
    oldfield = np.copy(dest.view(nicetype)['data'])
    dest['length'] = len(src)

    dest['data'] = "".join([char + '\x00' for char in src] + ['\x00\x00'])
    for i in range(len(src) * 2, dest.dtype['data'].itemsize):
        dest.view(nicetype)['data'][i] = oldfield[i]
        #dest['data'].view(np.character)[i] = oldfield[i]

def set_str8 (dest, src): # 16 or 8bit length, 8bit chars
    assert len (src) <= dest.dtype['value'].itemsize
    textlen = dest.dtype['value'].itemsize
    nicetype = np.dtype ([('length', dest.dtype['length']),('value', (np.uint8, textlen))])
    oldfield = np.copy(dest.view(nicetype)['value'])
    dest['length'] = len(src)

    dest['value'] = src + '\x00'
    for i in range(len(src), dest.dtype['value'].itemsize):
        dest.view(nicetype)['value'][i] = oldfield[i]
        #dest['value'].view(np.character)[i] = oldfield[i]

def set_str16 (dest, src): # 16bit/8bit len, 16bit chars, optionally unused field
    assert len (src) <= (dest.dtype['data'].itemsize / 2)
    dest['length'] = len(src)
    dest['data'] = "".join([char + '\x00' for char in src] + ['\x00\x00'])

def set_str8 (dest, src): # 16 or 8bit length, 8bit chars
    assert len (src) <= dest.dtype['value'].itemsize
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
