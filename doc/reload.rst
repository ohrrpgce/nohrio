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
'RELD\x01\r\x00\x00\x00\x14\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x01\x04root'


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

Child nodes
--------------

>>> root.add_child (r.Element('integerness', 999))
>>> root
Element ('root', None, [Element ('integerness', 999, [])])

>>> s = SIO()
>>> root.write_root(s)
>>> raw = s.getvalue()
>>> raw
'RELD\x01\r\x00\x00\x00\x1d\x00\x00\x00\x0c\x00\x00\x00\x01\x00\x01\x05\x00\x00\x00\x00\x02\xe7\x03\x00\x02\x0bintegerness\x04root'



Let's just check that:

RELD magic
01   version
13   header size
x1d  stringtable offset (0x1d = 29 decimal)
x0c   'root' element size (=12 decimal)
01   'root' tag
00   'root' type
01   'root' nchildren
05   'integerness' size
00   'integerness' tag
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
