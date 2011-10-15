import numpy as np
from numpy import int16 as INT
from numpy import int32 as LONG
from nohrio.lump import read_lumplist
import weakref


def text_lump_lines(f, offset, size):
    "An iterator over the lines in a lumped text file"
    f.seek (offset)
    left_to_read = offset + size - f.tell()
    while left_to_read > 0:
        line = f.readline()
        left_to_read = offset + size - f.tell()
        if left_to_read < 0:
            # Read too much from file, trim
            line = line[:left_to_read]
        yield line

def read_script_header(f, offset, size):
    info = {}
    f.seek (offset)
    data = f.read (4)
    header = np.ndarray ((1), dtype = 'i2, i2', buffer = data)
    info['data_off'] = header[0][0]
    info['numvars'] = header[0][1]
    info['numargs'] = None  # unknown
    info['version'] = 0
    info['strtable_off'] = 0
    info['strtable_size'] = 0
    info['flags'] = 0
    info['vartable_off'] = 0

    headerlen = min (info['data_off'], 22)
    if headerlen > 4:
        f.seek (offset)
        data = f.read (headerlen)
        # nearly everything defaults to 0
        data += '\0' * 22
        header = np.ndarray ((1), dtype = 'i2, i2, i2, i2, i4, i4, i2, i4', buffer = data)
        info['numargs'] = header[0][2]
        info['version'] = header[0][3]
        info['strtable_off'] = header[0][4]
        info['strtable_size'] = header[0][5]
        info['flags'] = header[0][6]
        info['vartable_off'] = header[0][7]

    if info['strtable_size'] == 0:
        info['strtable_size'] = size - info['strtable_off']

    if info['version'] == 0:
        info['int'] = INT
    else:
        info['int'] = LONG

    return info

def read_scripts_txt(f, offset, size):
    lines = text_lump_lines (f, offset, size)
    scriptnames = {}
    scriptids = {}
    for scriptname in lines:
        try:
            id = int (lines.next())
            args = int (lines.next())
            for i in range (args):
                lines.next()
        except StopIteration:
            raise IOError ('scripts.txt is corrupt')
        scriptname = scriptname.strip ()
        scriptnames[id] = scriptname
        scriptids[scriptname] = id
    return scriptnames, scriptids


def read_commands_bin(f, offset, size):
    f.seek (offset)
    data = f.read (size)
    header = np.ndarray ((1), dtype = 'i2, i2, i2', buffer = data)
    table_offset = header[0][0]
    version = header[0][1]
    numrecords = header[0][2]
    offsets = np.ndarray (shape = numrecords, dtype = INT, buffer = data, offset = table_offset)
    command_names = {}
    for cmdid, offset in enumerate(offsets):
        if offset:
            row = np.ndarray (shape = 2, dtype = INT, buffer = data, offset = offset)
            command_names[cmdid] = {'name': data[offset + 4 : offset + 4 + row[1]],
                                    'argnum': row[0]}
    return command_names
    

kNoop, kInt, kFlow, kGVar, kLVar, kMath, kCmd, kScript = range(8)
kinds_with_args = kFlow, kMath, kCmd, kScript
flowtypes = 'do', 'begin', 'end', 'return', 'if', 'then', 'else', 'for', 'while', 'break', 'continue', 'exitscript', 'exitreturning', 'switch', 'case'
mathcmds = 'random', 'exponent', 'modulus', 'divide', 'multiply', 'subtract', 'add', 'xor', 'or', 'and', 'equal', 'notequal', 'lessthan', 'greaterthan', 'lessthanorequalto', 'greaterthanorequalto', 'setvariable', 'increment', 'decrement', 'not', 'logand', 'logor', 'logxor', 'abs', 'sign', 'sqrt'
mathcmds_infix = '', '^', '%', '/', '*', '--', '+', 'xor', 'or', 'and', '==', '<>', '<', '>', '<=', '>=', ':=', '+=', '-=', '', '&&', '||', '^^', '', '', ''

class ScriptNode(object):

    def __init__(self, scripts, scriptinfo, offset):
        self.scripts = weakref.ref (scripts)
        self.scrinfo = scriptinfo
        self.scrdata = weakref.ref (scriptinfo['data'])
        self.offset = offset

    def _format(self, indent):
        kind = self.kind
        separator = ', '
        if kind == kNoop:
            return 'Noop'
        elif kind == kInt:
            return str(self.id)
        elif kind == kFlow:
            if self.id < 0 or self.id >= len (flowtypes):
                return 'BAD_FLOW(%d)' % self.id
            ret = flowtypes[self.id]
            separator = '\n' + ' ' * (indent + 2)
        elif kind == kGVar:
            return 'global%d' % self.id
        elif kind == kLVar:
            return 'local%d' % self.id
        elif kind == kMath:
            if self.id < 0 or self.id >= len (mathcmds):
                return 'BAD_MATH(%d)' % self.id
            if mathcmds_infix[self.id]:
                return '%s %s %s' % (self.arg (0), mathcmds_infix[self.id], self.arg (1))
            ret = mathcmds[self.id]
        elif kind == kCmd:
            ret = self.scripts().commandname (self.id)
        elif kind == kScript:
            ret = self.scripts().scriptnames [self.id]
        else:
            return 'BAD_NODE(kind=%d, id=%d)' % (self.kind, self.id)
        ret += '('
        pre = ''
        if kind == kFlow:
            pre = separator
        for arg in self.args ():
            ret += pre + arg._format(indent + 2)
            pre = separator
        if kind == kFlow and ret[-1] != '(':
            ret += '\n' + ' ' * indent
        return ret + ')'

    def __str__(self):
        return self._format(0)

    def _get_kind(self):
        return self.scrdata()[self.offset]

    def _get_id(self):
        return self.scrdata()[self.offset + 1]

    def _get_argnum(self):
        if self.kind not in kinds_with_args:
            return 0
        return self.scrdata()[self.offset + 2]

    def arg(self, i):
        return ScriptNode(self.scripts(), self.scrinfo, self.scrdata()[self.offset + 3 + i])

    def args(self):
        if self.kind not in kinds_with_args:
            return
        ret = ScriptNode(self.scripts(), self.scrinfo, 0)
        for i in range(self.argnum):
            ret.offset = self.scrdata()[self.offset + 3 + i]
            yield ret

    id = property (_get_id)
    kind = property (_get_kind)
    argnum = property (_get_argnum)


class HSScripts(object):

    def __init__(self, filename):
        self.file = open (filename, 'rb')
        self.manifest, self._lump_map = read_lumplist (self.file)
        if 'source.lumped' in self.manifest:
            self.source = 'source.lumped'
        elif 'source.txt' in self.manifest:
            self.source = 'source.txt'
        else:
            self.source = None
        self.scriptnames = {}
        self.scriptids = {}
        self._scriptcache = weakref.WeakValueDictionary ()
        try:
            lumpinfo = self._lump_map['scripts.txt']
        except KeyError:
            raise IOError ('scripts.txt lump missing')
        self.scriptnames, self.scriptids = read_scripts_txt (self.file, *lumpinfo)
        try:
            lumpinfo = self._lump_map['commands.bin']
        except KeyError:
            self.commands_info = {}
        else:
            self.commands_info = read_commands_bin (self.file, *lumpinfo)
 
    def __del__(self):
        self.file.close()

    def _load_script(self, lump):
        offset, size = self._lump_map[lump]
        scrinfo = read_script_header (self.file, offset, size)
        # It's actually quite hard to determine where the script data ends, so we load the whole lump
        length = (size - scrinfo['data_off']) / scrinfo['int']().nbytes
        scrinfo['data'] = np.memmap (self.file, mode = 'r', dtype = scrinfo['int'], shape = length, offset = offset + scrinfo['data_off'])
        return scrinfo

    def script(self, id_or_name):
        "Returns the root node of a script, or None if that script doesn't exist"
        if isinstance (id_or_name, int):
            id = id_or_name
        else:
            try:
                id = self.scriptids[id_or_name]
            except KeyError:
                return None
        if id in self._scriptcache:
            return self._scriptcache[id]
        lumpname = '%d.hsz' % id
        if lumpname not in self._lump_map:
            lumpname = '%d.hsx' % id
            if lumpname not in self._lump_map:
                return None
        scrinfo = self._load_script (lumpname)
        ret = ScriptNode (self, scrinfo, 0)
        self._scriptcache[id] = ret
        return ret

    def commandname(self, id):
        if id in self.commands_info:
            return self.commands_info[id]['name']
        return 'cmd%d' % id
