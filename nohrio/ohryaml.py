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
#
# representation plan
# simplified, v2:
#
# #. get the representation using SafeRepresenter.represent_data
# #. recursively descend, looking for MappingNodes which have exactly one key-value
#    pair, where the key is uppercase; that is node.value[0][0].value.isupper()
#    and len(node.value) == 1; find the corresponding dtype and reorder all key-value pairs
#    in this and sub-mappings according to it.
#    you can update node lists in place, YUS!
#    we also can reset the mapping flow_style to False or True according to number of keys.
#    aaand, reset 'binary' tagged items to 'str'

# #. serialize() the finalized nodes
#
# #. ROXEN!


lookup = {'GENERAL_DATA': 'gen',
          'NPCDEFS'  : 'n',
          'MAPNAMES' : 'mn',
          'NPCLOCS'  : 'l.linear',
          'MAPINFO'  : 'map',
          'PALETTE16' : 'pal',
          }

def partial_resort (node, dtype = None):
    """Deeply re-sort the nodes contained in node so they match dtype ordering.

    Notes
    -----

    keys are sorted in two separate sets; the set which contains
    keys mentioned in the dtype, and the set which doesn't.

    The first of these sets is sorted according to position in the dtype.
    The second is sorted alphabetically.
    Then they are concatenated (first + second), so
    all the important properties are written first.

    Dtypes are detected via key names, so partial_resort()
    can handle multiple different dtypes in a single document.

    Sorting is done **in place**. This has implications for recursion.

    """
    from yaml import MappingNode, SequenceNode
    from .ohrrpgce import dtypes, np
    if type (node) == MappingNode:

# when we are trying to find a node to identify with a dtype,
# operation is entirely recursive.

        if not dtype:
            for key, value in node.value:
                keycontent = key.value
                if keycontent.isupper and keycontent in lookup:
                    partial_resort (value, dtype = np.dtype (dtypes[lookup[keycontent]]))
                #elif keycontent in dtype.names and dtype[keycontent].char != 'V':
                #    partial_resort (value, dtype = dtype[keycontent])
        else:
            ordered = []
            unordered = []
            names = dtype.names
            for key, value in node.value:
                keycontent = key.value
                if keycontent == 'savoffset':
                    import pdb
                    pdb.set_trace()
                    print((key, value))
                if keycontent in names:
                    if type (value) == MappingNode:
                        partial_resort(value, dtype[keycontent])
                        ordered.append((key, value))
                    else:
                        # demangle strings-which-contained-non-ascii
                        if value.tag == 'tag:yaml.org,2002:binary':
                            value.value = value.value.decode('base64').encode('string_escape')
                            value.tag = 'tag:yaml.org,2002:str'
                            value.style = None
                        ordered.append((key, value))
                else:
                    unordered.append((key, value))
            ordered.sort (key = lambda v: names.index (v[0].value))
            unordered.sort ()
            node.value = ordered + unordered
    elif type (node) == SequenceNode:
        for value in node.value:
            partial_resort (value, dtype = dtype) # dtype is always None here?

def escape_node_strings (node):
    from yaml import MappingNode, SequenceNode
    if type (node) == MappingNode:
        for key, value in node.value:
            if value.tag == 'tag:yaml.org,2002:binary':
                value.value = value.value.decode('base64').encode('string_escape')
                value.tag = 'tag:yaml.org,2002:str'
                value.style = None
            elif value.tag == 'tag:yaml.org,2002:str':
                value.value = value.value.encode('string_escape')
            if type (value) in (MappingNode, SequenceNode):
                escape_node_strings (value)
    elif type (node) == SequenceNode:
        for childnode in node.value:
            escape_node_strings (childnode)

def unescape_object_strings (object):
    from yaml import MappingNode, SequenceNode
    if type(object) == dict:
        for key, value in object.items():
            if type(value) == str:
                object[key] = value.decode('string_escape')
            elif type(value) in (dict, list):
                unescape_object_strings(value)
    elif type(object) == SequenceNode:
        for item in object:
            unescape_object_strings(item)


# YAML dumping and loading
# -------------------------
#
# load() and dump() are wrappers around yaml.load and yaml.dump
# which handle necessary string value escaping automatically.

def load (string):
    # load yaml, demangle escaped strings
    from yaml import safe_load as load_
    data = load_(string)
    unescape_object_strings (data)
    return data

def dump (data):
    import yaml
    r = yaml.representer.SafeRepresenter()
    node = r.represent_data (data)
    partial_resort (node)
    escape_node_strings (node)
    return yaml.serialize (node)
    # escape strings, dump yaml

def find_dtype (mapping):
    for key in mapping.keys():
        if key in lookup:
            return key
    return None

def assign_array (array, value):
    from .ohrrpgce import set_str8, set_str16
    for key in array.dtype.names:
        if key in value:
            if array.dtype[key].names == None:
                # simple scalar assign
                array[key] = value[key]
            else:
                if (array.dtype[key].names[0] == 'length' and
                   array.dtype[key].names[-1] in ('value','data')):
                    double = array.dtype[key].names[-1] == 'data'
                    if double:
                        s = value[key][:array.dtype[key]['data'].itemsize / 2]
                        set_str16 (array[key], s)
                    else:
                        s = value[key][:array.dtype[key]['value'].itemsize]
                        set_str18 (array[key], s)
                else:
                    assign_array (array[key], value[key])

def py2array (object):
    """Convert one or more items (of the same dtype) to an array.

    object may look like either {'DTYPENAME':objectdata}
    (which translates to a scalar array -- shape == () ),
    or like [{'DTYPENAME':objectdata}, {'DTYPENAME':objectdata},..]
     (where all 'DTYPENAME' match. this is a 1d array -- shape == (len(object),) )
    """
    from .ohrrpgce import dtypes, np
    if type (object) == dict:
        # easy
        shape = ()
        dtype = find_dtype(object)
    elif type (object) == list:
        types = [type (v) for v in object]
        assert types.count(dict) == len (types)
        shape = len (object)
        dtype = find_dtype(object[0])
    if not dtype:
        raise ValueError('object doesn\'t seem to contain a record matching any dtype!')
    key_name = dtype
    dtype = np.dtype (dtypes[lookup [dtype]])
    array = np.zeros (shape = shape, dtype = dtype)
    if type (object) == dict:
        assign_array (array, object[key_name])
    elif type (object) == list:
        for i,item in enumerate (object):
            assign_array (array[i], item)
    return array


def print_pr (mapping):
    import yaml
    r = yaml.SafeRepresenter()
    node = r.represent_data (mapping)
    partial_resort (node)
    print(yaml.serialize (mapping))

def init ():
    from . import ohrrpgce
    import numpy as np
    for dtype in ohrrpgce.dtypes:
        dtype = np.dtype (dtype)

