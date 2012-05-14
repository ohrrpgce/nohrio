#!/usr/bin/env python
import sys
import os
import numpy as np
from nohrio.ohrstring import *
from nohrio.dtypes import dt
from nohrio.rpg2 import RPGDir

def concatenate(lists):
    return sum(lists, [])

def escaped_split(string, sep):
    """
    Split a line using a separator, but ignore separators between quotes
    """
    escaped = False
    ret = []
    piece = ""
    for char in string:
        if char == ',' and not escaped:
            ret.append(piece)
            piece = ""
        elif char == '"':
            escaped ^= True
            piece += char
        else:
            piece += char
    ret.append(piece)
    return ret

def escape_string(string):
    """
    Escape an 8-bit string suitably for an csv file

    Nonprintable characters are escaped in the same format that Custom's textbox
    exporter uses: '\ddd'
    """
    ret = '"'
    for c in string:
        if ord(c) <= 31 or ord(c) >= 127 or c == '"':
            if ord(c) == 10:
                ret += '\\n'
            else:
                ret += '\\%03d' % ord(c)
        else:
            ret += c
    return ret + '"'

def unescape_string(string):
    """
    Unescape a string from a typical csv file
    """
    temp = string.strip()
    if temp.startswith('"') and temp.endswith('"'):
        temp = temp[1:-1]
    
    ret = ""
    i = 0
    while i < len(temp):
        if temp[i:i+2] == '\\n':
            ret += '\n'
            i += 2
        else:
            try:
                if temp[i] == '\\':
                    ret += chr(int(temp[i+1:i+4]))
                    i += 3
                else:
                    ret += temp[i]
            except ValueError:
                ret += temp[i]
            i += 1
    return ret

def field_descriptor(dtype, name):
    """
    Given a (possibly compound) numpy dtype, return a (header, decoder, encoder) tuple for manipulating a flattened representation.

    Each field is flattened to N primitives (eg integers, strings).
    A header is a list of N (sub)field names.
    A decoder takes a field of an ndarray of type 'dtype' and returns a list of N ints/floats/strings
    An encoder has signature  encoder(dest, subfield, src)
    where  * 'dest' is a data field (either 0 dimensional ndarray of type 'dtype', or a regular
             array if 'dtype' is an array)
           * 'subfield' is an index in range(0, N), usually ignored
           * 'src' is a string, a single cell from a csv file
    and converts and writes 'src' into 'dest'

    Note: The flattening is similar to flatten_dtype in ohrrpgce.py.
    """
    ty = dtype #[name]
    if ty.isbuiltin:
        # Simple integer/float
        def decoder(src):
            return [src]
        def encoder(dest, subfield, src):
            # dereference
            dest[()] = src
        header = [name]

    elif ty.kind == 'S':
        # Raw string (as in textboxes)
        def decoder(src):
            return [escape_string(str(src))]
        def encoder(dest, subfield, src):
            dest[()] = unescape_string(src)
        header = [name]

    elif len(ty):
        # Compound field
        if ty.names[0] == 'length':
            # it's a string
            if ty.names[1] == 'value':
                # fvstr
                def decoder(src):
                    return [escape_string(get_str8(src))]
                def encoder(dest, index, src):
                    # TODO: warn if truncated
                    set_str8(dest, unescape_string(src))
            else:
                # vstr2 or funky 4 byte length variant
                def decoder(src):
                    return [escape_string(get_str16(src))]
                def encoder(dest, index, src):
                    # TODO: warn if truncated
                    set_str16(dest, unescape_string(src))
            header = [name]
        else:
            # Not primitive; recurse on subfields
            headers, decoders, encoders = zip(*
                [field_descriptor(ty[subfield], subfield) for subfield in ty.names]
                )

            def decoder(src):
                ret = []
                for i, d in enumerate(decoders):
                    ret.extend(d(src[i]))
                return ret
            def encoder(dest, index, src):
                for i, h in enumerate(headers):
                    if index < len(h):
                        field = ty.names[i]
                        encoders[i](dest[field], index, src)
                        break
                    index -= len(h)

            header = [name + ' ' + header for header in concatenate(headers)]
                
    elif len(ty.shape):
        # Array
        if len(ty.shape) == 1:
            _header, _decoder, _encoder = field_descriptor(ty.base, '')
        else:
            subdtype = np.dtype((ty.base, ty.shape[1:]))
            _header, _decoder, _encoder = field_descriptor(subdtype, '')
        def decoder(src):
            return concatenate(_decoder(a) for a in src)
        def encoder(dest, index, src):
            field_len = len(_header)
            newindex = index / field_len
            if len(ty.shape) == 1:
                reference = dest[newindex:newindex+1].reshape(())
            else:
                reference = dest[newindex]
            _encoder(reference, index % field_len, src)
        header = concatenate([['%s %d%s' % (name, i, piece) for piece in _header] for i in range(ty.shape[0])])

    else:
        print repr(ty)
        assert False

    return header, decoder, encoder

def lump2csv(lump, fields):
    """
    Returns a table in csv format containing a subset of the fields/columns and all the records/rows of a lump.

    'lump' is an ndarray, and fields is a list of field names of the lump's dtype.
    """
    fields = [name for name in fields if not name.startswith("unused")]
    headers2, decoders = [], []
    for name in fields:
        headers, decoder, encoder = field_descriptor(lump.dtype[name], name)
        headers2.extend(headers)
        decoders.append(decoder)
    ret = [','.join(headers2)]
    for item in lump:
        stuff = []
        for i, name in enumerate(fields):
            stuff.extend(decoders[i](item[name]))
        ret.append(','.join(str(a) for a in stuff))

    return '\n'.join(ret)


def csv2lump(csv, lump):
    """
    Parses a spreadsheet in csv format and writes into a ndarray of the right dtype.

    'csv' is string containing multiple lines where the first line contains column
    headers, and the remaining lines are records starting at 0.
    'lump' should have at least as many records as there in 'csv'
    """
    lines = csv.split('\n')
    present_headers = lines[0].split(',')
    records = [line for line in lines[1:] if len(line) > 0]

    if len(lump) != len(records):
        raise ValueError("csv table has %d records, but file has %d records" % (len(records), len(lump)))

    headers, encoders = [], []
    for fieldnum, name in enumerate(lump.dtype.names):
        _headers, _decoder, _encoder = field_descriptor(lump.dtype[name], name)
        headers.extend(_headers)
        encoders.extend( [(_encoder, name, i) for i in range(len(_headers))] )
    print

    encoder_list = []

    for header in present_headers:
        if header == '':
            encoder_list.append(None)
        try:
            encoder_num = headers.index(header.lower())
        except ValueError:
            raise ValueError("Could not recognise the column named '" + header + "'")
        encoder_list.append(encoders[encoder_num])

    print "Writing into records 0 to %d (out of %d existing)" % (len(records) - 1, len(lump))

    for recnum, csv_record in enumerate(records):
        # create a 0-dimensional reference to the record.
        # lump[recnum] returns an np.void object which is a *copy* of the original data
        record = lump[recnum:recnum+1].reshape(())

        fields = escaped_split(csv_record, ',')
        for i, datum in enumerate(fields):
            temp = encoder_list[i]
            if temp is None:
                continue
            encoder, fieldname, index = temp
            encoder(record[fieldname], index, datum)


if __name__ == '__main__':

    def usage():
        print "Usage:"
        print "  " + sys.argv[0] + " --type <type> --export <path_to_rpgdir> <csv_file>"
        print "  " + sys.argv[0] + " --type <type> --import <path_to_rpgdir> <csv_file>"
        print
        print " Where <type> is one of items, attacks, enemies, heroes, textboxes"
        print
        sys.exit(1)

    lumpnames = {'items': 'itm', 'enemies': 'dt1', 'heroes': 'dt0', 'attacks': 'attack.full', 'textboxes': 'say'}
    binsizes = {'items': 'item', 'enemies': None, 'heroes': 'hero', 'attacks': 'attack', 'textboxes': 'say'}

    if len(sys.argv) != 6:
        print "Not enough arguments"
        usage()

    if sys.argv[1] != '--type' or sys.argv[2] not in lumpnames:
        print "Type not understood"
        usage()
    lumpid = sys.argv[2]

    if sys.argv[3] == '--export':
        export = True
        mode = 'w'
    elif sys.argv[3] == '--import':
        export = False
        mode = 'r+'
    else:
        print "Specify --import or --export"
        usage()

    if not os.path.isdir(sys.argv[4]):
        print sys.argv[4] + " is not a directory"
        usage()

    rpg = RPGDir(sys.argv[4], 'r+')
    iofile = open(sys.argv[5], mode)

    def unsupported(msg, indicator, supported):
        msg += " (%d; expected %d)" % (indicator, supported)
        if indicator < supported:
            print msg + " The RPG file needs to be updated."
        else:
            print msg + " nohrio needs to be updated."
        sys.exit(1)
            
    rpgformat = rpg.data('gen').version
    if rpgformat not in (16, 17):
        unsupported("RPG file format not supported.", rpgformat, 17)

    if binsizes[lumpid]:
        lumpsize = dt[lumpnames[lumpid]].itemsize
        binsize = rpg.binsize[binsizes[lumpid]]
        if lumpid == 'attacks':
            binsize += 80
        if binsize != lumpsize: #ump.dtype.itemsize:
            unsupported("File format not supported: wrong binsize.", binsize, lumpsize)

    lump = rpg.data(lumpnames[lumpid])

    # If you're interested in all fields
    fields = lump.dtype.names

    if 0 and lumpid == 'items':
        # Only interested in some fields...
        fields = (
         'name',
         'info',
         'value',
         'attack',
         'weaponattack',
         'equippable',
        # 'teach',
        # 'oobuse',
         'weaponpic',
         'weaponpal',
         'bonuses',
        # 'equippableby',
        # 'bitsets',
         'consumability',
        # 'own_tag',
        # 'in_inventory_tag',
        # 'equipped_tag',
        # 'equippedby_active_tag',
        # 'frame2handle',
        # 'frame1handle',
        # 'elemdmg'
        )

    if export:
        iofile.write(lump2csv(lump, fields))
    else:
        #print lump.md5()
        # Operate on a copy so that nothing is done if an exception occurs
        lump2 = np.copy(lump)
        csv2lump(iofile.read(), lump2)
        lump[:] = lump2[:]
        #print lump.md5()
