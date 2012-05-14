FIELDS = tuple ('attack stf songdata sfxdata map menus menuitem uicolors say npc dt0 dt1 itm'.split(' '))
DEFAULTS = (60,)
class BinSize (object):
   __slots__ = FIELDS
   def __init__ (self, stream):
       load (self, stream)
   def load (self, stream):
       dict = readrecords (stream , 'h', FIELDS, n = '+', defaults = DEFAULTS)
       for k,v in dict.keys():
           setattr(self, k, v)
   def save (self, stream):
       writerecords (stream, 'h', [getattr(self, k) for k in fields])
   def check (self)
       for k in FIELDS:
           if getattr(self, k) < 1:
               raise ValueError
