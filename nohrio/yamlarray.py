# print array as nice YAML
# XXX to be robust, we should stop relying on numpy repr()
# and do our own slow, reliable printing.

import numpy as np

def fix_tuples (s):
    if '(' not in s and ')' not in s:
        return s
    import shlex
    finaltokens = []
    lasttoken = ''
    for token in shlex.shlex (s):
        if token not in ('(', ')', ','):
            finaltokens.append (token)
        elif token == '(':
            finaltokens.append ('[')
        elif token == ')':
            finaltokens.append (']')
        else:
            finaltokens.append (', ')
        if (lasttoken in (')', '}') or lasttoken.endswith ("'")) and token != ',':
            finaltokens.append (token + ', ')
            # add a comma
        lasttoken = token
    return "".join (finaltokens)

def dump_memmap (m):
    np.set_printoptions (threshold = 0xfffffff)
    import re
    result = []
    dtype = m.dtype
    for field in dtype.names:
        oldvalue = m[field]
        value = str (oldvalue)
        # this is going to err for strings containing commas.
        # use shlex instead.

        #value = re.sub ("([\\]\\)'0-9])+ ", lambda m:m.expand ('\\1, '), value)
        #value = re.sub ("([\\]\\)'])([\\[\\(\\n'])", lambda m:m.expand ('\\1, \\2'), value)

        #value = value.replace ('][','], [')
        #value = value.replace (')(','), (')
        #value = value.replace (')\n', '), ')
        #value = value.replace (']\n', '], ')
        if field == 'spells':
             print 'S', value
        #    # XXX handle deeper nesting.
        #    print 'F', field
        #    print 'V', oldvalue, '\t', value
        #    print 'S', oldvalue.dtype
        #try:
        #    if len (value) == 1: # scalar value
        #        value = repr (value[0])
        #    elif len (oldvalue) > 1:
        #        print ('SHAPED', oldvalue.shape)
        #        value = repr ([v.tolist() for v in oldvalue])
        #    else:
        #        print 'ESCAPE'
        #        value = repr (value)
        #except: #handle already-scalars
        ##    value = repr (value)
        # yaml doesn't understand tuples, automagic them into lists
        # use shlex so we don't mess with quoted text.
        value = fix_tuples (value)
        value = '%-20s : %s' % (field, value)
        # fix wasted 0s in uint16-based strings
        
        #if '\\x00' in value:
        #    value = value.replace ('\\x00','.')
        result.append (value)
    np.set_printoptions (threshold = 1000)
    return unicode("\n".join (result))


# XXX le tadji cnino
#
# relying on numpy printing is dodgy.
# we need to look directly at the array
# do our own primihi, effectively.

# hmm
#
# so, eg gen.tolist() provides a list of values for each field
# some subarrays may be included -- convert them into lists
# subarrays can also be expressed as tuples when sourced from memmaps
# so convert tuples to lists too.
# we then use dtype.names to convert the result into a vanilla Python dictionary (via 'dict (dtype.names, values)

#
# XXX we need to look at the dtype to assign fields correctly -- particularly, for data with sub-dtypes.
#
# hmmmmmmm..
#
# encode the dtype in the document?
# optional, but this will guarantee readability and arrayability!
#
# dtype only as an initial document for now.. KISS!
#

def python (map):
    dtype = map.dtype
    map = map.tolist()
    for i,v in enumerate (map):
        if type (v) == tuple:
            v = list(v)
            for i2, v2  in enumerate(v):
                if issubclass (type(v2), np.ndarray):
                    v2 = v2.tolist()
                    v[i2] = v2
            map[i] = v
        if issubclass (type(v), np.ndarray):
            map[i] = v.tolist()

def unpython (map, dtype):
    dest = np.zeros (shape = len (map), dtype = dtype)
    for name, value in items (map):
        pass

def issimpledtype (dtype):
    """Return True when the dtype is simple enough to be serialized in list(s) of one uniform type


    """
    # dtype = np.dtype (dtype)
    # only multi-field dtypes have names.
    # aggregates (eg 6*byte) don't, nor do scalars.
    if dtype.names:
        return False
    return True

def tuple2list (seq):
    """Convert tuples within the sequence into lists (recursively).
    The result is usually a sequence of lists.
    The actual toplevel container type is also converted into a list.
    """
    seq = list (seq)
    if len (seq) < 2:
        try:
            tmp = len (seq[0])
        except TypeError:
            # either no items, or the item is not of a sequence type
            return seq
    for i, v in enumerate (seq):
        try:
            tmp = len (v)
            if type (v) == str:
                continue
        except TypeError:
            continue
        seq[i] = tuple2list (v)
    return seq

def list2tuple (seq, level = 0):
    """Convert lists to tuples (except when the contents are all lists?)
    
    [[fieldname, fieldtype],
     [fieldname, fieldtype],
     [fieldname, [[fieldname, fieldtype], [fieldname, fieldtype]]],
    ]

     ->
    ((fieldname, fieldtype),
     (fieldname, fieldtype),
     (fieldname, [(fieldname, fieldtype), (fieldname, fieldtype)]))

    Appears to be an alternating pattern:

    nesting level 0 = tuple
    nesting level 1 = list
    nesting level 2 = tuple
    nesting level 3 = list
    ...
    
    """
    # need different, top-down implementation -- ti ka bottom-up
    seq = list (seq)
    for i, v in enumerate(seq):
        if type(v) in (list, tuple):
            #if level % 2 == 0:
            seq[i] = list2tuple(v, level = level + 1)
    if level % 2 == 1:
        return tuple (seq)
    return list (seq)

def dtype_document (dtype, version = -1):
    'return YAML serializing the given dtype into the header document.'
    import yaml
    dtype = np.dtype (dtype)
    return yaml.safe_dump ({'dtype' : tuple2list (dtype.descr), 'dtype_version': version})

def array2yaml (arr):
    if not issimpledtype (arr.dtype):
        raise NotImplemented('complex array serialization to YAML')
    import yaml
    return "\n---\n".join([dtype_document (arr.dtype),
                           yaml.safe_dump({'shape': list(arr.shape)}) +
                           yaml.safe_dump ({'data':arr.tolist()}) ])
    
    
def yaml2array (yaml):
    pass
