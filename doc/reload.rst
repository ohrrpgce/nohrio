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
