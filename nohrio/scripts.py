import numpy as np
from numpy import int16 as INT
from numpy import int32 as LONG
from nohrio.lump import read_lumplist, CorruptionError
import weakref
import hashlib


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

class Script(object):

    def __init__(self, scriptset, f, offset, size):
        self.scriptset = weakref.ref (scriptset)
        self.lump_size = size
        self._read_header (f, offset, size)
        # It's actually quite hard to determine where the script data ends, so we load the whole lump
        f.seek (offset + self.data_off)
        data = f.read (size - self.data_off)
        #self.data = np.memmap (f, mode = 'r', dtype = self.int, shape = length, offset = offset + self.data_off)
        cmds_len = self.cmds_size / self.int_bytes
        self.cmds = np.ndarray (buffer = data, dtype = self.int, shape = cmds_len, offset = 0)
        if self.strtable_size:
            self.strtable = np.ndarray (buffer = data, dtype = np.int8, shape = self.strtable_size, offset = self.strtable_off - self.data_off)
        else:
            self.strtable = None

    def __str__(self):
        if self.numargs is not None:
            numargs = self.numargs
            args = '(' + ', '.join('local%d' % i for i in range(self.numargs)) + ')'
        else:
            numargs = 0
            args = '(?)'
        ret = 'Script ' + self.name + args + '\n'
        if self.numvars:
            ret += 'variable(' + ', '.join('local%d' % i for i in range(numargs, self.numvars)) + ')\n'
        #ret += str(self.cmds) + '\n'
        ret += str(self.root()) + '\n'
        return ret

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
        expanded_cmds = np.array (self.cmds, dtype = np.int32)
        return self._md5 (expanded_cmds)

    def _read_header(self, f, offset, size):
        f.seek (offset)
        data = f.read (4)
        header = np.ndarray ((1), dtype = 'i2, i2', buffer = data)
        self.data_off = header[0][0]
        self.numvars = header[0][1]
        self.numargs = None  # unknown
        self.format_version = 0
        self.strtable_off = 0
        self.strtable_size = 0
        self.flags = 0
        self.vartable_off = 0

        headerlen = min (self.data_off, 28)
        if headerlen > 4:
            f.seek (offset)
            data = f.read (headerlen)
            # nearly everything defaults to 0
            data += '\0' * 28
            header = np.ndarray ((1), dtype = 'i2, i2, i2, i2, i4, i2, i2, i2, i4, i2, i4', buffer = data)
            self.numargs = header[0][2]
            self.format_version = header[0][3]
            self.strtable_off = header[0][4]
            self.parent = header[0][5]
            self.nesting_depth = header[0][6]
            self.num_nonlocals = header[0][7]
            self.strtable_size = header[0][8]
            self.flags = header[0][9]
            self.vartable_off = header[0][10]

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
            raise CorruptionError ('scripts.txt is corrupt')
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
flowtypes = 'do', 'begin', 'end', 'return', 'if', 'then', 'else', 'for', '!!FLOW8!!', '!!FLOW9!!', 'while', 'break', 'continue', 'exitscript', 'exitreturning', 'switch', 'case'
# How to print the different flow types
flow_oneline = 'return', 'break', 'continue', 'exitscript', 'exitreturning'
flow_withheader = 'if', 'while', 'switch' #'for'
# case and switch aren't handled nicely

# Math function nodes
kSetvariable, kIncrement, kDecrement = 16, 17, 18
mathcmds = 'random', 'exponent', 'modulus', 'divide', 'multiply', 'subtract', 'add', 'xor', 'or', 'and', 'equal', 'notequal', 'lessthan', 'greaterthan', 'lessthanorequalto', 'greaterthanorequalto', 'setvariable', 'increment', 'decrement', 'not', 'logand', 'logor', 'logxor', 'abs', 'sign', 'sqrt'
mathcmds_infix = '', '^', ',mod,', '/', '*', '--', '+', ',xor,', ',or,', ',and,', '==', '<>', '<', '>', '<=', '>=', ':=', '+=', '-=', '', '&&', '||', '^^', '', '', ''
math_precedence = 0, 20, 30, 30, 30, 40, 40, 60, 60, 60, 50, 50, 50, 50, 50, 50, 80, 80, 80, 0, 65, 70, 70, 0, 0, 0

class ScriptNode(object):

    def __init__(self, scriptset, script, offset):
        if not isinstance(scriptset, weakref.ref):
            scriptset = weakref.ref (scriptset)
        self.scriptset = scriptset
        self.script = script
        self.scrdata = weakref.ref (script.cmds)
        self.offset = offset

    def _is_infix(self):
        return self.kind == kMath and mathcmds_infix[self.id]

    def precedence(self):
        if self.kind != kMath:
            return 0
        return math_precedence[self.id]

    def _protected_arg(self, argnum):
        "String repr of one of the args, surrounded by brackets if required."
        child = self.arg(argnum)
        if self._is_infix() and child._is_infix():
            p1 = self.precedence()
            p2 = child.precedence()
            if p1 < p2 or (p1 == p2 and argnum == 1):
                return '(%s)' % child
        return '%s' % child

    def _format(self, indent):
        "Decompile to a string"
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
            oneline = ret in flow_oneline  # Print it like other statements, on one line
            withheader = ret in flow_withheader  # First arg is an expression, the rest are special
            separator = '\n' + ' ' * (indent + 2)
        elif kind == kGVar:
            return 'global%d' % self.id
        elif kind == kLVar:
            return 'local%d' % self.id
        elif kind == kMath:
            if self.id < 0 or self.id >= len (mathcmds):
                return 'BAD_MATH(%d)' % self.id
            if self.id in (kSetvariable, kIncrement, kDecrement):
                varid = self.arg (0)._get_id()
                if varid < 0:
                    varname = 'local%d' % (-1 - varid)
                else:
                    varname = 'global%d' % varid
                return '%s %s %s' % (varname, mathcmds_infix[self.id], self._protected_arg(1))
            elif mathcmds_infix[self.id]:
                return '%s %s %s' % (self._protected_arg(0), mathcmds_infix[self.id], self._protected_arg(1))
            ret = mathcmds[self.id]
        elif kind == kCmd:
            ret = self.scriptset().commandname (self.id)
        elif kind == kScript:
            ret = self.scriptset().scriptnames [self.id]
        else:
            return 'BAD_NODE(kind=%d, id=%d)' % (self.kind, self.id)
        ret += '('
        pre = ''
        if kind == kFlow and not oneline:
            pre = separator
            if withheader:
                pre = ''
            for idx, arg in enumerate(self.args ()):
                ret += pre + arg._format(indent + 2)
                if withheader and idx == 0:
                    ret += ')'
                pre = separator
            if not withheader:
                if ret[-1] != '(':
                    ret += '\n' + ' ' * indent
                ret += ')'
        else:
            for arg in self.args ():
                ret += pre + arg._format(indent + 2)
                pre = separator
            ret += ')'
        return ret

    def __str__(self):
        """Decompile to a string"""
        return self._format(0)

    def _get_kind(self):
        return int(self.scrdata()[self.offset])

    def _get_id(self):
        return int(self.scrdata()[self.offset + 1])

    def _get_argnum(self):
        if self.kind not in kinds_with_args:
            return 0
        return int(self.scrdata()[self.offset + 2])

    def arg(self, i):
        return ScriptNode(self.scriptset(), self.script, int(self.scrdata()[self.offset + 3 + i]))

    def args(self):
        if self.kind not in kinds_with_args:
            return
        for i in range(self.argnum):
            ret = ScriptNode(self.scriptset(), self.script, 0)
            ret.offset = int(self.scrdata()[self.offset + 3 + i])
            yield ret

    id = property (_get_id)
    kind = property (_get_kind)
    argnum = property (_get_argnum)


class HSScripts(object):

    # Public:
    #.scriptnames   : id -> scriptname dict
    #.scriptids     : scriptname -> id dict
    #.commands_info
    #.source

    def __init__(self, filename):
        self.file = open (filename, 'rb')
        self.manifest, self._lump_map = read_lumplist (self.file)
        if 'source.lumped' in self.manifest:
            self.source = 'source.lumped'
        elif 'source.txt' in self.manifest:
            self.source = 'source.txt'
        else:
            self.source = None
        self._scriptcache = weakref.WeakValueDictionary ()
        try:
            lumpinfo = self._lump_map['scripts.txt']
        except KeyError:
            raise CorruptionError ('scripts.txt lump missing')
        self.scriptnames, self.scriptids = read_scripts_txt (self.file, *lumpinfo)
        # scripts.txt may reference scripts which were declared (with definescript)
        # but aren't present. It's still possible for them to be called from in other
        # scripts, but maybe these should be removed from scriptnames?
        try:
            lumpinfo = self._lump_map['commands.bin']
        except KeyError:
            self.commands_info = {}
        else:
            self.commands_info = read_commands_bin (self.file, *lumpinfo)
 
    def close(self):
        self.file.close()
        # Try to free references to the memmaps
        #for script in self._scriptcache.itervalues():
        #    script.drop_data()

    def __del__(self):
        self.close()

    def _load_script(self, id):
        lumpname = '%d.hsz' % id
        if lumpname not in self._lump_map:
            lumpname = '%d.hsx' % id
            if lumpname not in self._lump_map:
                return None
        offset, size = self._lump_map[lumpname]
        script = Script (self, self.file, offset, size)
        script.id = id
        script.name = self.scriptnames[id]
        return script

    def _remove_from_cache(self, script):
        for k, v in self._scriptcache.iteritems ():
            if v is script:
                del self._scriptcache[k]
                return

    def script(self, id_or_name):
        "Returns a Script object given either id or normalised name, or None if that script doesn't exist"
        if isinstance (id_or_name, int):
            id = id_or_name
        else:
            try:
                id = self.scriptids[id_or_name]
            except KeyError:
                return None
        if id in self._scriptcache:
            return self._scriptcache[id]
        else:
            script = self._load_script (id)
            if script:
                self._scriptcache[id] = script
            return script

    def commandname(self, id):
        if id in self.commands_info:
            return self.commands_info[id]['name']
        return 'cmd%d' % id
