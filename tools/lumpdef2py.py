#!/usr/bin/env python
import yaml

META = {}

class Compiler (object):
    def __init__ (self, filename):
        self.source_filename = filename
        f = open (filename, 'rb')
        self.source = yaml.safe_load (f)
        f.close ()
        self.classify ()
    def classify (self):
        d = self.source
        self.helperdata = {}
        [d[k] for k in d.keys() if k == k.upper()]
        self.dtypeinfo = {}
        for k, v in d.items():
            if k == k.upper():
                self.helperdata[k] = v
            elif k == k.lower():
                self.dtypeinfo[k] = v
            else:
                print ('unknown data kind %r = %r' % (k, v))

from pprint import pprint

c = Compiler ('lumpdefs.yaml')
pprint (c.dtypeinfo)#(c.helperdata)

