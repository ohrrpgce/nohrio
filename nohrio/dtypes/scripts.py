import struct
from nohrio.iohelpers import Filelike, IOHandler, readstr, writestr
import numpy as np

#ported from TMC's rpgbatch branch

INT = np.dtype('<i2')
LONG = np.dtype('<i4')


def unpackonly(fmt, data):
    return struct.unpack(fmt, data[:struct.calcsize(fmt)])

def read_commands_bin(fh):
    data = fh.read()
    table_offset, version, numrecords = unpackonly('<3h', data)
    offsets = np.ndarray(shape=numrecords, dtype=INT, buffer=data, offset=table_offset)
    command_names = {}
    for cmdid, offset in enumerate(offsets):
        if offset:
            nargs, namelen = unpackonly('<2h', data[offset:])
            name = data[offset + 4 : offset + 4 + namelen].encode('utf8')
            command_names[cmdid] = {'name': name,
                                    'argnum': nargs}
    return command_names

def read_scripts_txt(f, size):
    lines = text_lump_lines(f, size)
    scriptnames = {}
    scriptids = {}
    for scriptname in lines:
        try:
            id = int(lines.next())
            args = int(lines.next())
            for i in range(args):
                lines.next()
        except StopIteration:
            raise CorruptionError ('scripts.txt is corrupt')
        scriptname = scriptname.strip ()
        scriptnames[id] = scriptname
        scriptids[scriptname] = id
    return scriptnames, scriptids

class Script(object):

    def __init__(self, scriptset, fh, size):
        self.scriptset = weakref.ref(scriptset)
        self.lump_size = size
        self._read_header (fh, size)
        # It's actually quite hard to determine where the script data ends, so we load the whole lump
        fh.seek (self.data_off)
        data = fh.read (size - self.data_off)
        #self.data = np.memmap (f, mode = 'r', dtype = self.int, shape = length, offset = offset + self.data_off)
        cmds_len = self.cmds_size / self.int_bytes
        self.cmds = np.ndarray (buffer = data, dtype = self.int,
                                shape = cmds_len, offset = 0)
        if self.strtable_size:
            self.strtable = np.ndarray (buffer = data, dtype = np.int8,
                                        shape = self.strtable_size,
                                        offset = self.strtable_off - self.data_off)
        else:
            self.strtable = None

    def drop_data(self):
        "Delete script data from this object, preserving just metadata about the script"
        del self.cmds
        del self.strtable
        if self.scriptset():
            self.scriptset()._remove_from_cache (self)

    def root(self):
        "Returns the root ScriptNode"
        return ScriptNode (self.scriptset, self, 0)

    def _md5(self, cmds):
        md5 = hashlib.md5 ()
        md5.update (cmds)
        if self.strtable != None:
            md5.update (self.strtable)
        return md5.digest ()

    def md5(self):
        return self._md5 (self.cmds)

    def invariate_md5(self):
        "A (slow) alternative to md5() which returns identical hashes for 16- and 32-bit versions of a script"
        if self.int_bytes == 4:
            return self.md5 ()
        expanded_cmds = self.cmds.astype(LONG)
        return self._md5 (expanded_cmds)

    def _read_header(self, f, size):
        data = f.read (4)
        self.data_off, self.numvars = struct.unpack('<2h', data)
        self.numargs = None  # unknown
        self.format_version = 0
        self.strtable_off = 0
        self.strtable_size = 0
        self.flags = 0
        self.vartable_off = 0

        headerlen = min(self.data_off, 22)
        if headerlen > 4:
            f.seek(0, 0)
            data = f.read(headerlen)
            # nearly everything defaults to 0
            data += '\0' * 22
            header = unpackonly('<hhhhiihi', data)
            (self.numargs,
             self.format_version,
             self.strtable_off,
             self.strtable_size,
             self.flags,
             self.vartable_off) = header

        if self.format_version == 0:
            self.int = INT
            self.int_bytes = 2
        else:
            self.int = LONG
            self.int_bytes = 4

        # It's actually quite nontrivial to determine where the script data ends
        # FIXME: the following is incorrect for scripts compiled with 'hspeak4' HSpeak branch, but
        # luckily no such scripts exist in the wild
        if self.strtable_off:
            self.cmds_size = self.strtable_off - self.data_off
            if self.strtable_size == 0:
                self.strtable_size = size - self.strtable_off
        else:
            self.cmds_size = size - self.data_off
            self.strtable_size = 0

# ScriptNode, HSScripts not here yet.

### XXX the above is not verified correct or even runnable.
### porting in progress.


class ScriptNames(dict, IOHandler):
    def __init__(self, source):
        if isinstance(source, dict):
            self.update(source)
            return
        with Filelike(source, 'rb') as fh:
            while 1:
                try:
                    id = unpackint(fh)
                    name = readstr(fh, 2, 1, 36)
                    self[id] = name
                except IOError:
                    break # no more data
    def _save(self, fh):
        for id in sorted(self.keys()):
            name = self[id]
            packint(fh, id)
            writestr(fh, name, 2, 1, 36)

class ScriptTriggers(list, IOHandler):
    def __init__(self, source):
        if isinstance(source, (list, tuple)):
            self[:] = source
            return
        with Filelike(source, 'rb') as fh:
            while 1:
                try:
                    scriptid = unpackint(fh)
                    name = readstr(fh, 2, 1, 36)
                    self.append = (scriptid, name)
                except IOError:
                    break # no more data
    def _save(self, fh):
        for scriptid, name in self:
            packint(fh, scriptid)
            writestr(fh, name, 2, 1, 36)

class Script(IOHandler):
    def __init__(self, source)
        # read header = [<h hdrsize, nvars(??, nargs, scriptver, <i strtable_offset, <i strtable_len,
        #                BITSETS[16] bitsets, <I localvarstrtable_offset ??)]
        # if format is 0 or 1, strtable_offset is the final field and it's a <h.
        # read raw script data as a blob (for now.)
        # read string table (0 or more of 2,1+s (plus padding between items to 4-byte boundaries)
        3
        #
        pass # copy some stuff from TMC's implementation

class ScriptCollection(IOHandler):
    def __init__(self, source):
        pass
        # read HS sublump: literal "HamsterSpeak", <h version = 3, 2s subversion?
        # read SCRIPTS.TXT: text lines [name, id, nargs, defaultargs(or arg-enumeration if HSpeak <2I)
        #  OR - read SCRIPTS.BIN: header = [<h hdrsize, recsize], record+=[<h id, triggertype, 2,1*36s name]
        # read COMMANDS.BIN: header = [<h hdrsize == 6, fmtversion, nrecords],
        #                    offsettable[$nrecords] = [<h position],
        #                    funcrecord@offsettable[index] = [<h nargs (-1 if variable), 2,1*+s name]
        # index all HSX/HSZ, sanity check their non/existence
        # read SOURCE.TXT as a gzipped binary blob,
        #   OR SOURCE.LUMPED as a gzipped binary blob.
        #
        # don't handle SRCFILES for now
        #
    def __getitem__(self, k):
        if k not in self.index:
            raise ValueError('Script
