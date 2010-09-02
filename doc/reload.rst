Reload document loading/saving
==============================


Basic empty document
----------------------

>>> import nohrio.reload as r

>>> root = r.Element('root')

>>> root
Element ('root', None, [])

>>> from cStringIO import StringIO as SIO
>>> s = SIO()
>>> root.write_root(s)

>>> raw = s.getvalue()
>>> raw
'RELD\x01\r\x00\x00\x00\x14\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x01\x04root'

4 bytes magic + 1 byte version + 4 bytes header size + 4 byte string table offset (... =13 bytes)
+
4 bytes node size + 1 byte tag name + 1 byte type + 0 bytes data + 1 byte children count (... =7 bytes)
+
1 byte nstrings + 1 byte 'root' length + 4 bytes 'root' (... = 6 bytes)

13+7 = 20 + 6 = 26

>>> len (raw)
26

>>> s = SIO(raw)
>>> root2 = r.read(s)
>>> root2
Element ('root', None, [])

>>> root == root2
True

(just testing that comparing non-equivalent nodes does indeed result in False)

>>> root != r.Element ('root', 0, [])
True

>>> root != r.Element ('root', '', [])
True

Child nodes
--------------

>>> root.add_child (r.Element('integerness', 999))
>>> root
Element ('root', None, [Element ('integerness', 999, [])])

>>> s = SIO()
>>> root.write_root(s)
>>> raw = s.getvalue()
>>> raw
'RELD\x01\r\x00\x00\x00\x1d\x00\x00\x00\x0c\x00\x00\x00\x02\x00\x01\x05\x00\x00\x00\x01\x02\xe7\x03\x00\x02\x0bintegerness\x04root'


Let's just check that:

RELD magic
01   version
13   header size
x1d  stringtable offset (0x1d = 29 decimal)
x0c   'root' element size (=12 decimal)
02   'root' tag
00   'root' type
01   'root' nchildren
05   'integerness' size
01   'integerness' tag
02   'integerness' type (2 == short int)
x3e7 'integerness' value (999)
00   'integerness' nchildren
02   nstrings
xb   len('integerness')
STR  'integerness'
04   len('root')
STR  'root'

:D

>>> root2 = r.read (SIO (raw))
>>> root2
Element ('root', None, [Element ('integerness', 999, [])])

>>> root2 == root
True

Differently typed child nodes
------------------------------

>>> for name, value in zip ('abcdefg', (None, -56, 32767, -1048576, 2**48, 99.99, 'ko pilno do')):
...     root.add_child (r.Element(name, value))

BTW: the None type, as the RELOAD page says, is usable as a child node -- the entire
node acts as a flag (of whatever the node name specifies.)

>>> root #doctest: +NORMALIZE_WHITESPACE
Element ('root', None, [Element ('integerness', 999, []), Element ('a', None, []),
Element ('b', -56, []), Element ('c', 32767, []), Element ('d', -1048576, []),
Element ('e', 281474976710656L, []), Element ('f', 99.989999999999995, []),
Element ('g', 'ko pilno do', [])])

>>> s = SIO()
>>> root.write_root(s)
>>> raw = s.getvalue()
>>> raw
'RELD\x01\r\x00\x00\x00q\x00\x00\x00`\x00\x00\x00\t\x00\x08\x05\x00\x00\x00\x08\x02\xe7\x03\x00\x03\x00\x00\x00\x01\x00\x00\x04\x00\x00\x00\x03\x01\xc8\x00\x05\x00\x00\x00\x02\x02\xff\x7f\x00\x07\x00\x00\x00\x05\x03\x00\x00\xf0\xff\x00\x0b\x00\x00\x00\x04\x04\x00\x00\x00\x00\x00\x00\x01\x00\x00\x0b\x00\x00\x00\x07\x05\x8f\xc2\xf5(\\\xffX@\x00\x0f\x00\x00\x00\x06\x06\x0bko pilno do\x00\t\x01a\x01c\x01b\x01e\x01d\x01g\x01f\x0bintegerness\x04root'

>>> s = SIO(raw)
>>> root2 = r.read(s)
>>> root2 #doctest: +NORMALIZE_WHITESPACE
Element ('root', None, [Element ('integerness', 999, []), Element ('a', None, []),
Element ('b', -56, []), Element ('c', 32767, []), Element ('d', -1048576, []),
Element ('e', 281474976710656L, []), Element ('f', 99.989999999999995, []),
Element ('g', 'ko pilno do', [])])

>>> root2 == root
True

>>> r.reload_from_dict ({'solar': None, 'flares' :
... { 'are': 10, 'unorange': 1/3.}, 'and': None, 'called': 'solar flares'},'root') #doctest: +NORMALIZE_WHITESPACE
Element ('root', None, [Element ('and', None, []), Element ('called', 'solar flares', []),
Element ('flares', None, [Element ('are', 10, []),
Element ('unorange', 0.33333333333333331, [])]), Element ('solar', None, [])])


Multiple same-named child nodes
--------------------------------

>>> root = r.Element ('root')
>>> root.add_child (r.Element('foo',1))
>>> root.add_child (r.Element('foo',2))
>>> root
Element ('root', None, [Element ('foo', 1, []), Element ('foo', 2, [])])

>>> root2 = r.Element ('root')
>>> root2.add_child (r.Element('foo',2))
>>> root2.add_child (r.Element('foo',1))
>>> root2
Element ('root', None, [Element ('foo', 2, []), Element ('foo', 1, [])])

These two trees are not necessarily equivalent in meaning.

>>> root == root2
False

But when node order is unimportant, they should be.
For this application, we have fuzzy_eq ()

>>> root.fuzzy_eq (root2)
True


(further checking that when node content is different, not just reordered, things
compare as different.)

>>> root.children[0].data = 99

>>> root.fuzzy_eq (root2)
False

>>> root == root2
False
