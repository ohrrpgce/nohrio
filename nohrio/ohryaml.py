# serialization of YAML
# =====================

yaml_fixes = {
  'pal': {'__inline' : True}
}


# when length+data pairs (complex string) are separated layout-wise
# (eg spell list names in dt0), we need to perform special measures to
# get the lengths updated correctly (the YAML-stored lengths are ignored.)

def scalar (array):
    """Convert a 0-dim array to an appropriate scalar.

    Complex numbers and other types that are not canonical to YAML
    are rejected."""
    code = array.dtype.char
    if code in 'bBcChHiI':
        return int (array)
    elif code in 'fg':
        return float (array)
    elif code in 'S':
        return str (array) # these need special serialization if
        # they contain non-ascii numbers -- explicitly specify 'str' tag
    elif code in 'V':
        # length, value complex string
        try:
            return str (array['value'][:array['length']])
        except:
            # icky 16bit characters
            return str (array['data'][::2][:array['length']])

    raise ValueError()

def array2py (array):
    if array.dtype.char != 'V':
        # non-complex dtypes -> sequences or scalars
        # XXX handle length, content strings appropriately (they are scalars)
        if array.ndim == 0:
            return scalar (array)
        else:
            result = []
            for item in array:
                if item.ndim > 1:
                    # handle multi-dimensional arrays of simple types
                    result.append (array2py(item))
                elif item.ndim == 1:
                    result.append ([scalar(v) for v in item])
                else:
                    result.append (scalar (item))
            return result
    else:
        # complex dtype
        if array.ndim >= 1:
            return [array2py (item) for item in array]
        elif (array.dtype.descr[0][0] == 'length' and array.dtype.descr[-1][0] in ('data','value')):
            try:
                return str (array['value'][:array['length']])
            except:
                # icky 16bit characters
                return str (array['data'][::2][:array['length']])
        result = {}
        for field in array.dtype.descr:
            fieldname = field[0]
            result[fieldname] = array2py (array[fieldname])
        return result


# convert an array2py'ed array to nodes
# ======================================

def init ():
    import ohrrpgce
    import numpy as np
    for dtype in ohrrpgce.dtypes:
        dtype = np.dtype (dtype)

