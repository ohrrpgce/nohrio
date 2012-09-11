from unittest import TestCase
import nose
import functools
from oktest import ok
import os
import numpy as np
dtype = np.dtype

from bits.dtypemapping import dtype_coverage, owners
from bits.dtype import DType

def test(dt):
    print (dtype_coverage(dt))
    print (dt)

def test2(dt):
    print (owners(dt, 0))
    print (dt)

for func in test, test2:
    func(dtype('4f4'))
    func(DType ('<h:x:h:y:4xh:z:').freeze())
    func(DType ('<T{h:x:h:y:}:coords:4xh:z:').freeze())
    func(DType ('<T{h:x:xx}:coords:4xh:z:').freeze())

