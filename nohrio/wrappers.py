"""Wrapper classes for ndarray,
   to provide nice eg map[0].doors.x[0] access.

"""
from numpy import memmap, ndarray
import numpy as np

class md5Array (ndarray):
    def md5 (self):
        from hashlib import md5
        return md5(self.data).hexdigest()

class OhrData (md5Array):
    def __getattr__ (self, k):
        dt = self.dtype.names
        if dt and k in dt:
            return self[k]
        else:
            return super(OhrData, self).__getattribute__ (k)
    def __setattr__ (self, k, v):
        dt = self.dtype.names
        if dt and k in dt:
            self[k] = v
        else:
            super(OhrData, self).__setattr__ (k, v)
    def __hasattr__ (self, k):
        dt = self.dtype.names
        return (dt and k in dt)
    def fields (self):
        return self.dtype.names()
#    def __array_finalize__ (self, obj):
#        if hasattr (obj, '__dict__'):
#            self.__dict__.update (obj.__dict__)

class OhrDataMemmap (OhrData, memmap):
    pass

class AttackData (OhrData):
    # virtualization of the awkward attack data format,
    # that needs "stapling together"
    # when that is deleted or flush()ed, the data gets rewritten to disk.

    def __new__ (cls, dt6, attack_bin, dtype):
        """
        dt6 and attack_bin should be memmaps for those two lumps (or None if attack.bin not present)
        """
        # Yes, you are meant to construct ndarray subtypes in __finalize_array__ instead
        # of in __new__, but we don't want that: only the top level object, not any views
        # into it, has special logic

        self = super(AttackData, cls).__new__ (cls, len(dt6), dtype = dtype)

        if attack_bin is not None:
            assert len(dt6) == len(attack_bin)
            attack_binsize = attack_bin.dtype.itemsize
            self._attack_bin = attack_bin.view((np.uint8, attack_binsize))
        else:
            attack_binsize = 0

        self._dt6 = dt6.view((np.uint8, 80))
        extraspace = dtype.itemsize - dt6.itemsize - attack_binsize
        self._masking_dtype = np.dtype([('dt6', np.uint8, 80), ('attack.bin', np.uint8, attack_binsize), ('extra', np.uint8, extraspace)])

        byteview = self.view (self._masking_dtype)
        byteview['dt6'] = self._dt6
        if attack_bin is not None:
            byteview['attack.bin'] = self._attack_bin
        byteview['extra'] = 0
        return self

    def _flush (self):
        self._dt6[:] = self.view (self._masking_dtype)['dt6']
        if hasattr (self, '_attack_bin'):
            self._attack_bin[:] = self.view (self._masking_dtype)['attack.bin']

    def __del__ (self):
        # Note that __del__ is called on slices too
        if hasattr (self, '_dt6'):
            self._flush()


# automagical virtual dtype hacks for planar data follow :)
class NpcLocData (memmap, md5Array):
    def _get_x (self):
        return self[...,0]
    def _set_x (self, v):
        self[...,0] = v
    def _get_y (self):
        return self[...,1]
    def _set_y (self, v):
        self[...,1] = v
    def _get_id (self):
        return self[...,2]
    def _set_id (self, v):
        self[...,2] = v

    def _get_dir (self):
        return self[...,3]
    def _set_dir (self, v):
        self[...,3] = v
    def _get_frame (self):
        return self[...,4]
    def _set_frame (self, v):
        self[...,4] = v

    x = property (_get_x,_set_x)
    y = property (_get_y,_set_y)
    id = property (_get_id,_set_id)
    dir = property (_get_dir,_set_dir)
    frame = property (_get_frame,_set_frame)

class DoorLinks (memmap, md5Array):
    def _get_src (self):
        return self[...,0]
    def _set_src (self, v):
        self[...,0] = v
    def _get_dest (self):
        return self[...,1]
    def _set_dest (self, v):
        self[...,1] = v
    def _get_destmap (self):
        return self[...,2]
    def _set_destmap (self, v):
        self[...,2] = v
    def _get_tag1 (self):
        return self[...,3]
    def _set_tag1 (self, v):
        self[...,3] = v
    def _get_tag2 (self):
        return self[...,4]
    def _set_tag2 (self, v):
        self[...,4] = v

    src = property (_get_src,_set_src)
    dest = property (_get_dest,_set_dest)
    destmap = property (_get_destmap,_set_destmap)
    tag1 = property (_get_tag1,_set_tag1)
    tag2 = property (_get_tag2,_set_tag2)

class DoorDefs (memmap, md5Array):
    def _get_x (self):
        return self[...,0]
    def _set_x (self, v):
        self[...,0] = v
    def _get_y (self):
        return self[...,1]
    def _set_y (self, v):
        self[...,1] = v
    def _get_bitsets (self):
        return self[...,2].astype('H')
    def _set_bitsets (self, v):
        self[...,2] = np.asarray(v).astype('H')

    x = property (_get_x,_set_x)
    y = property (_get_y,_set_y)
    bitsets = property (_get_bitsets,_set_bitsets)

### end planar hacks

packed_image_guesses = {
    5120 : (8, 32, 40),
    578 :  (34, 34),
    1250:  (50, 50),
    3200:  (80, 80),
    1600:  (8, 20, 20),
    576:   (2, 24, 24),
    3750:  (3, 50, 50),
    2048:  (16, 16, 16),}

class PackedImageData (OhrDataMemmap):
    def unpack (self, dest = None, shape = None, transpose = None):
        if not shape:
            if self.shape[-1] in packed_image_guesses:
                shape = packed_image_guesses[self.shape[-1]]
            else:
                shape = self.shape
        # convert 4bpp -> 8bpp
        part2 = self & 0xf
        part1 = (self & 0xf0) >> 4
        newshape = shape
        if not dest:
            unpacked = np.empty (shape = newshape, dtype = np.uint8)
        else:
            unpacked = dest
        unpacked.flat[0::2] = part1
        unpacked.flat[1::2] = part2
        # transpose dimensions appropriately.
        if transpose:
            if transpose == 'xy':
                transpose = list (range (unpacked.ndim))
                transpose [-2:] = [transpose[-1], transpose[-2]]
                unpacked = np.transpose (unpacked, transpose)
            else:
                unpacked = np.transpose (unpacked, transpose)
        return unpacked

def pack (src, dest = None, transpose = None):
    """Pack 8bpp image(s) with <=16 colors into a 4bpp image.

    Optionally transpose the output.
    """
    if transpose:
        if transpose == 'xy':
            transpose = list (range (src.ndim))
            transpose [-2:] = [transpose[-1], transpose[-2]]
            src = np.transpose (src, transpose)
        else:
            src = np.transpose (src, transpose)
    # check whether the input fits in this array...
    if src.shape[-1] % 2:
        raise ValueError ('width %d is not an even number of pixels.' % src.shape[-1])
    nsrcpixels = src.nbytes
    if dest:
        ndestpixels = dest.nbytes * 2
        if nsrcpixels != ndestpixels:
            raise ValueError (
              '%d byte unpacked image cannot be packed into a %d byte destination!' %
              (nsrcpixels, ndestpixels))
        if (src.shape[:-1] + (src.shape[-1] / 2)) != dest.shape:
            raise ValueError (
              '%d byte pitch doesn\'t fit exactly %d pixels' %
              (dest.shape[-1], src.shape[-1] / 2))
    else:
        dest = np.zeros (shape = src.shape[:-1] + (src.shape[-1] / 2,), dtype='B')
    if src.max() > 15:
        raise ValueError ('source image should only contain indices [0...15]')
    # Take two source pixels, pack them into one destination pixel
    res = dest
    #return
    part2 = src.flat[0::2] << 4
    part1 = src.flat[1::2]
    res.flat[:] = part1
    res.flat[:] |= part2
    return res
    #raise NotImplementedError('pack')
    # reverse the above transform

__all__ = ('md5Array','AttackData','NpcLocData','DoorLinks','DoorDefs','OhrData','OhrDataMemmap','pack','PackedImageData')
