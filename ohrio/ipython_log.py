#log# Automatic Logger file. *** THIS MUST BE THE FIRST LINE ***
#log# DO NOT CHANGE THIS LINE OR THE TWO BELOW
#log# opts = Struct({'__allownew': True, 'logfile': 'ipython_log.py'})
#log# args = []
#log# It is safe to make manual edits below here.
#log#-----------------------------------------------------------------------
import pixlab.image.cairo as pic
pic.cairo
from pylab import draw, subplot, imshow, show
import scipy.ndimage as sni
ins, ina = pic.surface_and_array (64, 64, pic.cairo.FORMAT_A8)
mcedit /home/ion/py/pixlab/pixlab/image/cairo.py
_ip.system("mcedit /home/ion/py/pixlab/pixlab/image/cairo.py")
pic = reload (pic)
ins, ina = pic.surface_and_array (64, 64, pic.cairo.FORMAT_A8)
ins, ina = pic.surface_and_array (pic.cairo.FORMAT_A8, 64, 64)
_ip.system("mcedit /home/ion/py/pixlab/pixlab/image/cairo.py")
pic = reload (pic)
ins, ina = pic.surface_and_array (pic.cairo.FORMAT_A8, 64, 64)
_ip.magic("pdb ")
pic = reload (pic)
ins, ina = pic.surface_and_array (pic.cairo.FORMAT_A8, 64, 64)
_ip.system("mcedit /home/ion/py/pixlab/pixlab/image/cairo.py")
pic = reload (pic)
ins, ina = pic.surface_and_array (pic.cairo.FORMAT_A8, 64, 64)
_ip.system("mcedit /home/ion/py/pixlab/pixlab/image/cairo.py")
pic = reload (pic)
ins, ina = pic.surface_and_array (pic.cairo.FORMAT_A8, 64, 64)
_ip.system("mcedit /home/ion/py/pixlab/pixlab/image/cairo.py")
pic = reload (pic)
ins, ina = pic.surface_and_array (pic.cairo.FORMAT_A8, 64, 64)
ins
ina
mcedit /home/ion/py/pixlab/pixlab/image/cairo.py
_ip.system("mcedit /home/ion/py/pixlab/pixlab/image/cairo.py")
pic = reload (pic)
ins, ina = pic.surface_and_array (pic.cairo.FORMAT_A8, 64, 64)
ins
ina
ina.shape
ina.shape = (64,64)
ina
_ip.system("mcedit /home/ion/py/pixlab/pixlab/image/cairo.py")
import cairo
c = cairo.Context (ins)
c.set_antialias (cairo.ANTIALIAS_NONE)
c.set_line_width(0.5)
c.set_source_rgba (1,1,1,1)
c.move_to (0,0)
c.line_to (63,16)
c.line_to (16,63)
c.stroke()
ina
imshow(ina);draw()
imshow(ina, interpolation = None);draw()
draw()
show()
c.set_line_width(1)
c.move_to (0,0)
c.line_to (16,63)
c.line_to (63,16)
c.stroke()
gray()
from pylab import draw, subplot, imshow, show, gray
gray()
imshow(ina, interpolation = None);draw()
imshow(ina, interpolation = 'nearest');draw()
outa = sni.convolve(ina, weights)
weights = np.zeros ((3,3), 'B')
weights [0,2] = 1
weights [1,1] = 1
weights [2,0] = 1
weights
outa = sni.convolve(ina, weights)
imshow(outa, interpolation = 'nearest');draw()
weights[...] = 0
weights[1] = 1
outa = sni.convolve(ina, weights)
imshow(outa, interpolation = 'nearest');draw()
#?sni.grey_dilation
imshow(ina, interpolation = 'nearest');draw()
imshow(outa, interpolation = 'nearest');draw()
#?sni.convolve
outa = sni.convolve(ina, weights, origin = 1)
outa = sni.convolve(ina, weights, origin = (0,1))
imshow(outa, interpolation = 'nearest');draw()
imshow(ina, interpolation = 'nearest');draw()
imshow(outa, interpolation = 'nearest');draw()
outa = sni.convolve(ina, weights, origin = (1,0))
imshow(outa, interpolation = 'nearest');draw()
weights
weights[1] = 4
weights[0] = 2
weights[2] = 2
outa = sni.convolve(ina, weights)
imshow(outa, interpolation = 'nearest');draw()
outa
outa = sni.convolve(ina, weights/ 24.)
outa
imshow(outa, interpolation = 'nearest');draw()
weights
weights[...] = 0
weights[0,2] = 1
weights[1,1] = 1
weights[2,0] = 1
imshow(outa, interpolation = 'nearest');draw()
outa = sni.convolve(ina, weights/ 3.)
imshow(outa, interpolation = 'nearest');draw()
weights
weights[0,0] = 1
weights[2,2] = 1
outa = sni.convolve(ina, weights/ 5.)
imshow(outa, interpolation = 'nearest');draw()
imshow(outa, interpolation = 'nearest');draw()
imshow(ina, interpolation = 'nearest');draw()
imshow(outa, interpolation = 'nearest');draw()
c.move_to(10,20)
c.line_to(16,50),
c.stroke()
imshow(ina, interpolation = 'nearest');draw()
outa = sni.convolve(ina, weights/ 5.)
imshow(outa, interpolation = 'nearest');draw()
subplot(211)
imshow(ina, interpolation = 'nearest');draw()
subplot(212)
imshow(outa, interpolation = 'nearest');draw()
show()
from pylab import draw, subplot, imshow, show, gray, jet
jet()
draw()
show()
#?sni.correlate
outa = sni.correlate (ina, weights / 5.0)
imshow(outa, interpolation = 'nearest');draw()
show()
gray()
draw()
weights[...] = 1
outa = sni.correlate (ina, weights / 9.0)
imshow(outa, interpolation = 'nearest');draw()
outa = sni.binary_closing(ina)
imshow(outa, interpolation = 'nearest');draw()
outa = sni.binary_opening(ina)
imshow(outa, interpolation = 'nearest');draw()
outa = sni.binary_closing(ina)
imshow(outa, interpolation = 'nearest');draw()
outa - ina
imshow(ina - outa, interpolation = 'nearest');draw()
imshow(outa, interpolation = 'nearest');draw()
outa
ina - outa
ina ^ outa
imshow(ina ^outa, interpolation = 'nearest');draw()
outa = sni.binary_closing(ina)
imshow(ina ^outa, interpolation = 'nearest');draw()
outa = sni.binary_opening(ina)
imshow(ina ^outa, interpolation = 'nearest');draw()
outa - ina
imshow(ina -outa, interpolation = 'nearest');draw()
imshow(outa - ina -outa, interpolation = 'nearest');draw()
imshow(outa * ina , interpolation = 'nearest');draw()
imshow(outa / ina , interpolation = 'nearest');draw()
imshow(ina / outa , interpolation = 'nearest');draw()
imshow(ina * outa , interpolation = 'nearest');draw()
imshow(ina ** outa , interpolation = 'nearest');draw()
imshow(outa **ina, interpolation = 'nearest');draw()
outa = sni.grey_opening (ina)
outa = sni.grey_opening (ina, size = 3)
outa = sni.grey_opening (ina, size = (3,3))
imshow(outa **ina, interpolation = 'nearest');draw()
imshow(outa, interpolation = 'nearest');draw()
outa = sni.grey_closing (ina, size = (3,3))
imshow(outa, interpolation = 'nearest');draw()
outa = sni.binary_erosion (ina)
imshow(outa, interpolation = 'nearest');draw()
outa = sni.convolve(ina, weights/ 9.)
imshow(outa, interpolation = 'nearest');draw()
weights
weights[1,1] = 2
outa = sni.convolve(ina, weights/ 10.)
imshow(outa, interpolation = 'nearest');draw()
weights[1,1] = 8
sum(weights)
outa = sni.convolve(ina, weights/ 16.)
imshow(outa, interpolation = 'nearest');draw()
outa[10,30]
outa[10:16,30]
outa[10:16,30:40]
outa = sni.convolve(ina, weights/ 8.)
imshow(outa, interpolation = 'nearest');draw()
imshow(outa, interpolation = 'nearest');draw()
weight
weights
outa = sni.correlate(ina, weights/ 8.)
imshow(outa, interpolation = 'nearest');draw()
outa = sni.correlate(ina, weights/ 4.)
imshow(outa, interpolation = 'nearest');draw()
outa = sni.correlate(ina, weights/ 1.)
imshow(outa, interpolation = 'nearest');draw()
weights[(0,2),(0,2)] = 0
weights
weights [0,2]
weights [2,0]
outa = sni.correlate(ina, weights/ 1.)
imshow(outa, interpolation = 'nearest');draw()
outa = sni.correlate(ina, weights/ 8.)
imshow(outa, interpolation = 'nearest');draw()
outa = sni.correlate(ina, weights/ 4.)
imshow(outa, interpolation = 'nearest');draw()
outa = sni.correlate(ina, weights/ 12.)
imshow(outa, interpolation = 'nearest');draw()
outa = sni.correlate(ina, weights/ 10.)
imshow(outa, interpolation = 'nearest');draw()
outa = sni.correlate(ina, weights/ 9.)
imshow(outa, interpolation = 'nearest');draw()
outa = sni.correlate(ina.astype('f'), weights/ 9.)
imshow(outa, interpolation = 'nearest');draw()
outa = sni.correlate(ina.astype('f'), weights/ 4.)
imshow(outa, interpolation = 'nearest');draw()
outa = sni.correlate(ina.astype('f'), weights/ 2.)
imshow(outa, interpolation = 'nearest');draw()
outa = sni.correlate(ina, weights/ 13)
imshow(outa, interpolation = 'nearest');draw()
outa = sni.correlate(ina, weights/ 13.)
imshow(outa, interpolation = 'nearest');draw()
jet()
draw()
show()
min(outa)
outa.min()
outa.max()
outa[30]
import pixlab.vector.potrace as pvp
#?pvp.savePGM
ina
pvp.savePGM (ina, '/tmp/trace.pgm')
#?pvp.PoTracer
#?pvp.potrace
#?pvp.potrace?
mcedit /home/ion/py/pixlab/pixlab/vector/potrace.py
_ip.system("mcedit /home/ion/py/pixlab/pixlab/vector/potrace.py")
pvp = reload (pvp)
#?pvp.potrace
res = pvp.potrace (ina, alpha = 0.6)
res
result = pvp.loadPGM (res)
result
draw()
draw()
imshow(outa, interpolation = 'nearest');draw()
imshow(result, interpolation = 'nearest');draw()
tmpa = np.zeros((66,66), dtype ='B')
tmpa[1:-1,1:-1] = ina
res.close()
res = pvp.potrace (tmpa, alpha = 0.6)
result = pvp.loadPGM (res)[1:-1,1:-1]
imshow(result, interpolation = 'nearest');draw()
gray()
draw()
imshow((result / 1.0) ** 2.2, interpolation = 'nearest');draw()
imshow((result / 1.0) ** (1/2.2), interpolation = 'nearest');draw()
res.close()
res = pvp.potrace (tmpa, alpha = 0.0)
result = pvp.loadPGM (res)[1:-1,1:-1]
imshow((result / 1.0) ** (1/2.2), interpolation = 'nearest');draw()
show()
weights
imshow(sni.binary_dilate(ina), interpolation = 'nearest');draw()
imshow(sni.binary_dilation(ina), interpolation = 'nearest');draw()
imshow(sni.binary_dilation(ina) - ina, interpolation = 'nearest');draw()
draw()
draw()
edgemasked = sni.binary_dilation(ina) - ina 
ina
127 in ina
ina[:,:4]
edgemasked
draw()
show()
draw()
draw()
draw()
draw()
draw()
imshow(edgemasked, interpolation = 'nearest');draw()
draw()
edgemasked2 = edgemasked.copy*(
)
edgemasked2 = edgemasked.copy()
weights
draw()
draw()
draw()
edgemasked[10:20,0:10]
edgemasked[8:22,0:10]
edgemasked[7:22,0:10]
edgemasked[6:22,0:10]
edgemasked[6:22,0:10]
edgemasked[8:22,0:10]
edgemasked[8:22,3:10]
edgemasked[8:20,3:10]
edgemasked[8:20,3]
len(edgemasked[8:20,3])
weights = np.zeros (5, 'B')
weights
weights[...] = 1
weights
weights = np.zeros (7, 'B')
weights[...] = 1
weights[...] = 1
weights
ina[8:20, 3]
len(ina[8:20, 3])
len(ina[8:20, 3])
sni.convolve1d? 
#?sni.convolve1d
res2 = sni.convolve1d (ina[8:20, 3], weights / 5.)
res2
resa = ina.copy()
resa[8:20,3] = sni.convolve1d (ina[8:20, 3], weights / 5.)
subplot (211)
imshow(resa, interpolation = 'nearest');draw()
show ()
_ip.magic("pdb ")
resb = sni.convolve1d (ina[8:20, 3], weights / 5.)
resb
resb *= (255/204.)
resb
resa[8:20,3] = resb
imshow(resa, interpolation = 'nearest');draw()
imshow(((resa / 255.0) ** (1/2.2)) * 255, interpolation = 'nearest');draw()
show()
weights
resb = sni.convolve1d (ina[8:20, 3], weights[:-1] / 6.)
resa[8:20,3] = resb
imshow(((resa / 255.0) ** (1/2.2)) * 255, interpolation = 'nearest');draw()
show()
resb = sni.convolve1d (ina[8:20, 3], weights[:-1] / 3.)
resa[8:20,3] = resb
imshow(((resa / 255.0) ** (1/2.2)) * 255, interpolation = 'nearest');draw()
resb
resb = sni.convolve1d (ina[8:20, 3], weights[:-1] / 4.)
resb
len(weights)
_ip.magic("logstart ")

_ip.magic("pwd ")
#?sni.convolve1d
resb = sni.convolve1d (ina[8:20, 3], weights[:-1] / 6., mode = 'extend')
resb = sni.convolve1d (ina[8:20, 3], weights[:-1] / 6., mode = 'nearest')
resb
resb = sni.convolve1d (ina[8:20, 3], weights / 7., mode = 'nearest')
resb
resb = sni.convolve1d (ina[8:20, 3], weights[:-1] / 4., mode = 'nearest')
resb
resb = sni.convolve1d (ina[8:20, 3], weights[:-1] / 4., mode = 'constant')
resb
len(resb)
resb = sni.convolve1d (ina[8:20, 3], weights[:-1] / 4.)
resb
ina[8:20,3]
tmp =ina[8:20,3]
tmp[:6]
sni.convolve (tmp[:6], weights[:-1])
sni.convolve (tmp[:6], weights[:-1] / 4)
sni.convolve (tmp[:6], weights[:-1] / 4.)
sni.convolve (tmp[:6], weights[:-1] / 5.)
sni.convolve (tmp[:6], weights[:-1] / 3.)
sni.convolve (tmp[:6], weights[:-1] / 4.)
sni.convolve (tmp[:6], weights / 4.)
sni.convolve (tmp[:6], weights / 4.)
weights.resize(8)
weights = np.resize (weights, 8)
sni.convolve (tmp[:6], weights / 4.)
sni.convolve (tmp[:6], weights[:-2] / 4.)
sni.convolve (tmp[:6], weights[:-3] / 4.)
sni.convolve1d (tmp[:6], weights[:-3] / 4.)
#?sni.convolve1d
sni.convolve1d (tmp[:6], weights[:-3] / 4., origin = 1)
sni.convolve1d (tmp[:6], weights[:-3] / 4., origin = 2)
sni.convolve1d (tmp[:6], weights[:-3] / 4., origin = 3)
sni.convolve1d (tmp[:6], weights[:-3] / 4., origin = -1)
sni.convolve1d (tmp[:6], weights[:-3] / 4., origin = 0)
sni.convolve1d (tmp[:6], weights[:-3] / 5., origin = 0)
sni.convolve1d (tmp[:6], weights[:-3] / 6., origin = 0)
tmp
sni.convolve1d (tmp[:6], weights[:-3] / 6., origin = 0)
weights
len (weights[:-3]
)
sni.convolve1d (tmp[:6], weights[:-2] / 6., origin = 0)
sni.convolve1d (tmp[:6], weights[:-3] / 6., origin = 0)
sni.convolve1d (tmp[:6], weights[:-2] / 6., origin = 0)
sni.convolve1d (tmp[:6], weights[:-2] / 6., origin = 0, mode = 'wrap')
sni.convolve1d (tmp, weights[:-2] / 6., origin = 0, mode = 'wrap')
sni.convolve1d (tmp, weights[:-2] / 4., origin = 0, mode = 'wrap')
sni.convolve1d (tmp, weights[:-2] / 4., origin = 1, mode = 'wrap')
sni.convolve1d (tmp, weights[:-2] / 4., origin = -1, mode = 'wrap')
sni.convolve1d (tmp, weights[:-2] / 4., origin = -.5, mode = 'wrap')
sni.convolve1d (tmp, weights[:-2] / 4., mode = 'wrap')
sni.convolve1d (tmp, weights[:-2] / 2., mode = 'wrap')
sni.convolve1d (tmp, weights[:-2] / 1., mode = 'wrap')
sni.convolve1d (tmp, weights[:-2] / 8., mode = 'wrap')
sni.convolve1d (tmp, weights[:-2] / 8., mode = 'wrap')
#?sni.generic_filter
weights
weights[:] = [1,2,4,8,4,2,1]
weights[:-1] = [1,2,4,8,4,2,1]
sni.convolve1d (tmp, weights[:-1] / 22., mode = 'wrap')
tmp = sni.convolve1d (tmp, weights[:-1] / 22., mode = 'wrap')
tmp
resb = tmp
resa[8:20,3] = resb * (255. / 208)
imshow(((resa / 255.0) ** (1/2.2)) * 255, interpolation = 'nearest');draw()
show()
weights[:-1] = [1,2,3,4,3,2,1]
tmp = sni.convolve1d (tmp, weights[:-1] / 16., mode = 'wrap')
tmp
resb = tmp
resa[8:20,3] = resb * (255. / resb.max())
imshow(((resa / 255.0) ** (1/2.2)) * 255, interpolation = 'nearest');draw()
show()
resa
resb * (255. / resb.max())
int (resb * (255. / resb.max()))
(resb * (255. / resb.max())).astype('B')
show()
weights[:-1] = 1
weights[:-1].sum()
tmp = sni.convolve1d (tmp, weights[:-1] / 7., mode = 'wrap')
tmp
resb = tmp
resa[8:20,3] = resb * (255. / resb.max())
tmp = sni.convolve1d (tmp, weights[:-1] / 6., mode = 'wrap')
tmp
tmp = sni.convolve1d (tmp, weights[:-1] / 8., mode = 'wrap')
tmp
tmp = sni.convolve1d (tmp, weights[:-1] / 12., mode = 'wrap')
tmp
tmp = sni.convolve1d (tmp, weights[:-1] / 4., mode = 'wrap')
tmp
tmp = sni.convolve1d (tmp, weights[:-1] / 7., mode = 'wrap')
tmp
tmp = ina[8:20, 3]
resb = sni.convolve1d (tmp, weights[:-1] / 7., mode = 'wrap')
resb
resb = sni.convolve1d (tmp, weights[:-1] / 6., mode = 'wrap')
resb
resb = sni.convolve1d (tmp, weights[:-1] / 8., mode = 'wrap')
resb
resb = sni.convolve1d (tmp, weights[:-1] / 6., mode = 'wrap')
resb
resb = sni.convolve1d (tmp, weights[:-1] / 5., mode = 'wrap')
resb
resb = sni.convolve1d (tmp, weights[:-1] / 4., mode = 'wrap')
resb
weights[:-1]
weights = np.ones (10) / 10.
weights
resb = sni.convolve1d (tmp, weights, mode = 'wrap')
resb
weights = np.ones (8)
weights
resb = sni.convolve1d (tmp, weights/ 4, mode = 'wrap')
resb
resb = sni.convolve1d (tmp, weights/ 3, mode = 'wrap')
resb
resb = sni.convolve1d (tmp, weights/ 5, mode = 'wrap')
resb
tmp
