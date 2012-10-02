from nohrio.iohelpers import Filelike, IOHandler, readstr, writestr

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
