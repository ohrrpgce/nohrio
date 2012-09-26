from nohrio.iohelpers import IOHandler, Filelike
from bits import AttrStore, UnwrappingArray
from bits.dtype import DType
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

class FormationData(IOHandler):
    dtype = DType("8T{<h:type:h:x:h:y:h:unused:}:enemies:T{<h:bg:h:music:h:bgframes:h:bgspeed:4h:unused:}:info:").freeze()
    def __init__(self, source):
        d = self
        with Filelike(source) as fh:
            data = fh.read (d.dtype.itemsize)
            s = np.fromstring(data, dtype=d.dtype, count = 1).reshape(())
            s = s.view(UnwrappingArray)
            d.info = AttrStore(**{k:s['info'][i] for i,k in enumerate(('bg', 'music', 'bgframes', 'bgspeed', 'unused'))})
            d.info.unused = d.info.unused.tolist()
            d.enemies = [AttrStore(**{k:subs[i] for i,k in enumerate(('type','x','y','unused'))}) for subs in s['enemies']]
            #for e in d.enemies:
            #    e.unused = e.unused.tolist()

    def _save(self, dest):
        with Filelike(dest) as fh:
            writeasarr(self.enemies, 'type x y unused', '<h, <h, <h, <h', fh)
            writeasarr(self.info, 'bg music bgframes bgspeed unused', '<h, <h, <h, <h, <4h', fh)

if __name__ == "__main__":
    fh = open('../../ohrrpgce/vikings/vikings.rpgdir/viking.for', 'rb')
    fh.seek (FormationData.dtype.itemsize*3)
    #print (fh.read(FormationData.dtype.itemsize))
    f = FormationData(fh)
    print (f.enemies)
    print (f.info)
    f.save('/tmp/foo.for')
    f2 = FormationData('/tmp/foo.for')
    #print(f2.enemies)
    print(f.info == f2.info)