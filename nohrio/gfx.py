def shape_bpp_adjust (shape, bpp = 4, srcbpp = 8):
    """Return an appropriate shape for a reduced/increased bitdepth image

    Examples
    ---------
    4bpp pixels (default) take up half a byte each:
    >>> shape_bpp_adjust ((4, 16, 16))
    (4, 16, 8)

    2bpp pixels take up a quarter of a byte each
    >>> shape_bpp_adjust ((4, 16, 16), bpp = 2)
    (4, 16, 4)

    if you want to convert back:

    >>> shape_bpp_adjust ((4, 16, 4), srcbpp = 2, bpp = 8)
    (4, 16, 16)

    """
    assert bpp in (8,4,2,1)
    return shape[:-1] + (int (shape[-1] / (float(srcbpp) / bpp )),)

def reduce_shape (shape):
    i = 1
    for value in shape:
        i *= value
    return i

def hex_4bpp_array (array):
    "convert a 4bpp array to hex string"
    if array.ndim > 3 or array.ndim < 2:
        raise ValueError ('array must be either (y,x) or (z,y,x) shape')


def pack_array (array, bpp = 8, srcbpp = 4):
    pass

# repack_array?

def unpack_array (array, srcbpp = 4):
    "unpack an array to 8bpp"
    nparts = 8 / srcbpp
    masks = [1 << srcbpp - 1]
    shifts = [srcbpp * v for i in range (nparts)]
    for i in range (1, nparts):
        masks.append (masks[-1] << (srcbpp * i))
    newshape = shape_bpp_adjust (array.shape, bpp = 8, srcbpp = 4)
    size = reduce_shape (newshape)
    unpacked = np.zeros (shape = (size,), dtype = np.uint8)
    for i, mask, shift in zip (range (nparts), masks, shifts):
        unpacked.flat[i::nparts] = (array & mask) << shift
    return unpacked

def unpack_4bpp_array (array):
    """convert a 4bpp array [.., h, w/2] -> [.., h, w]

    Examples
    --------

    >>> import numpy as np

    Unpack a 4x4 4bpp image, stored in a 4x2 array

    >>> arr = np.array([[0xff,    0], [   0, 0xff],
    ...                 [ 0xf,  0xf], [0xf0, 0xf0]], dtype='B')

    >>> unpack_4bpp_array (arr)
    array([[15, 15,  0,  0],
           [ 0,  0, 15, 15],
           [15,  0, 15,  0],
           [ 0, 15,  0, 15]], dtype=uint8)

    Notes
    ------

    The resultant array always has an even-length last dimension.

    """
    import numpy as np
    part1 = array & 0xf
    part2 = (array & 0xf0) >> 4
    newshape = shape_bpp_adjust (array.shape, bpp = 8, srcbpp = 4)
    size = reduce_shape (newshape)
    unpacked = np.empty (shape = (size,), dtype = np.uint8)
    unpacked.flat[0::2] = part1
    unpacked.flat[1::2] = part2
    unpacked.shape = newshape
    return unpacked

