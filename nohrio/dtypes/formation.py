from nohrio.iohelpers import IOHandler, Filelike
from nohrio.dtypes.tag import TagCheckClass
from bits import AttrStore, UnwrappingArray
from bits.dtype import DType
from bits.enum import Enum, MultiRange
from numpy import dtype
import numpy as np

def writeasarr(obj, attrs, _dtype, fh):
    shape = ()
    try:
        len(obj)
        shape = len(obj)
    except:
        pass
    if type(attrs) == str:
        attrs = attrs.split()
    if type(_dtype) != dtype:
        _dtype = dtype(_dtype)
    arr = np.zeros(shape, dtype=_dtype)
    for n in range(0, shape or 1):
        this = arr
        that = obj
        if shape:
            this = arr[n]
            that = obj[n]
        for i, k in enumerate(attrs):
            this[_dtype.names[i]] = getattr(that, k)
    fh.write(arr.tostring())
    #arr.tofile(fh)

def writeasleints(fh, *items):
    totalsize = sum(1 if type(v) == int else len(v) for v in items)
    d = np.empty(totalsize, dtype = '<h')
    index = 0
    for item in items:
        if type(item) == int:
            d[index] = item
            index += 1
        else:
            for v in item:
                d[index] = v
                index += 1
    fh.write(d.tostring())

class FormationRef(Enum):
    valid = MultiRange(((0,32767),))

class FormationData(IOHandler):
    dtype = DType("8T{<h:type:h:x:h:y:h:unused:}:enemies:T{<h:bg:h:music:h:bgframes:h:bgspeed:4h:unused:}:info:").freeze()
    def __init__(self, source):
        d = self
        with Filelike(source, 'rb') as fh:
            data = fh.read (d.dtype.itemsize)
            s = np.fromstring(data, dtype=d.dtype, count = 1).reshape(())
            s = s.view(UnwrappingArray)
            d.info = AttrStore(**{k:s['info'][i] for i,k in enumerate(('bg', 'music', 'bgframes', 'bgspeed', 'unused'))})
            d.info.unused = d.info.unused.tolist()
            d.enemies = [AttrStore(**{k:subs[i] for i,k in enumerate(('type','x','y','unused'))}) for subs in s['enemies']]
            #for e in d.enemies:
            #    e.unused = e.unused.tolist()

    def _save(self, dest):
        s = self
        with Filelike(dest, 'rb') as fh:
            writeasarr(s.enemies, 'type x y unused', '<h, <h, <h, <h', fh)
            writeasarr(s.info, 'bg music bgframes bgspeed unused', '<h, <h, <h, <h, <4h', fh)

def _load (cls, fh):
    cls(fh)

FormationData._load = _load.__get__(FormationData)

class FormationSetData(IOHandler, AttrStore):
    dtype = DType('<h:frequency:20h:entries:h:tagcheck:3h:unused:').freeze()
    class tagdummyclass(object):
        filename = 'fs'
    def __init__(self, source):
        d = self
        with Filelike(source, 'rb') as fh:
            data = fh.read (d.dtype.itemsize)
            s = np.fromstring(data, dtype=d.dtype, count=1).reshape(())
            s = s.view(UnwrappingArray)
            d.frequency = s['frequency']
            d.entries = s['entries'].tolist()
            d.tagcheck = TagCheckClass(FormationSetData.tagdummyclass)(s['tagcheck'])
            d.unused = s['unused'].tolist()

    def _save(self, dest):
        s = self
        with Filelike(dest, 'wb') as fh:
            writeasleints(fh, s.frequency, s.entries,
                             int(s.tagcheck), s.unused)
    def __eq__(self, y):
        if not isinstance(y, __class__):
            return False
        return all(getattr(self, k) == getattr (y, k)
                   for k in ('frequency', 'entries', 'tagcheck', 'unused'))


if __name__ == "__main__":
    fh = open('../../ohrrpgce/vikings/vikings.rpgdir/viking.for', 'rb')
    fh.seek (FormationData.dtype.itemsize*3)
    #print (fh.read(FormationData.dtype.itemsize))
    f = FormationData(fh)
    print (f.enemies)
    print (f.info)
    fs = FormationSetData('../../ohrrpgce/vikings/vikings.rpgdir/viking.efs')
    print(fs.entries)
    from io import BytesIO
    bio = BytesIO()
    fs.save(bio)
    bio = BytesIO(bio.getvalue())
    fs2 = FormationSetData(bio)
    print (fs == fs2)
    f.save('/tmp/foo.for')
    f2 = FormationData('/tmp/foo.for')
    #print(f2.enemies)
    print(f.info == f2.info)