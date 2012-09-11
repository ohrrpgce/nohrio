#!/usr/bin/env python3
from unittest import TestCase
import nose
import functools
from oktest import ok
from nohrio.nohrio2 import rpg_creator, create
import os
from tempfile import mktemp # yeah unsafe, I know.

def md5(filename):
    """Test helper: Return the md5sum of a given file"""
    #XXX will be slower on windows; use hashlib instead on windows.
    from subprocess import check_output
    return check_output(['md5sum', filename]).decode('utf8').split(' ')[0]
temp = functools.partial (mktemp, prefix='nohrio',dir='/tmp')

# XXX get setup/teardown working so we don't leave truckloads of directories hanging around.

def rm_rpgdir (path):
    import glob
    assert path.startswith('/tmp')
    for filename in glob.glob (os.path.join(path, '*')):
        os.remove (filename)
    os.rmdir (path)

class CreateTest(TestCase):
    create = rpg_creator(template = 'ohrrpgce.rpgdir')
    _empty2b = 'c4103f122d27677c9db144cae1394a66'
    expected = (('archinym.lmp', (20, 160), None),
                ('browse.txt', 80, 'bbf7c6077962a7c28114dbd10be947cd'),
                ('binsize.bin', (26,36), None),
                ('fixbits.bin', (3,16), None),
                ('defpal0.bin', 2, _empty2b),
                ('defpal1.bin', 2, _empty2b),
                ('defpal2.bin', 2, _empty2b),
                ('defpal3.bin', 2, _empty2b),
                ('defpal4.bin', 2, _empty2b),
                ('defpal5.bin', 2, _empty2b),
                ('defpal6.bin', 2, _empty2b),
                ('defpal7.bin', 2, _empty2b),
                ('defpal8.bin', 2, _empty2b),
                ('menus.bin', 0, 'd41d8cd98f00b204e9800998ecf8427e'),
                ('menuitem.bin', 576, 'c902a375900924151268a40b8f851fac'),
                ('songdata.bin', 32, '70bc8f4b72a86921468bf8e8441dce51'),
                ('uicolors.bin', (126, 200), None),
                ('palettes.bin', 772, None),
                ('attack.bin', 546, '7051431ecf48fc136230d9d9e67b2817'),
                ('*.gen', 1007, None),
                ('*.d00', 2007, 'bf70937e5a4061b40ff56ea7a0c61b39'),
                ('*.dox', 12000, '21d9938f335c6bfab0eeaed58673b073'),
                ('*.dt0', 51480, '287a71ebaba1f8fe40ebc3994b1250ab'),
                ('*.dt1', 734, 'd344650f36d58d207436fde9b5d05f03'),
                ('*.dt6', 80, 'a514443a1551245dea0efaa23356bd41'),
                ('*.e00', 715, '0465c30d0f958dd9b4dc3a29cf984799'),
                ('*.efs', 100, '6d0bb00954ceb7fbee436bb55a8397a9'),
                ('*.fnt', 2055, None),
                ('*.for', 80, 'bbf7c6077962a7c28114dbd10be947cd'),
                ('*.itm', 1260, 'afd34f2e6a05b7ad20a78d933ba69f15'),
                ('*.l00', 3007, '997f89d36bbf8d2dcc340471afe281b3'),
                ('*.map', 68, None),
                ('*.mas', 1543, None),
                ('*.mn', 80, 'bbf7c6077962a7c28114dbd10be947cd'),
                ('*.mxs', 64000, 'f5a2e8660d886e4b1225ffdbaf9eb33b'),
                ('*.n00', 3407, '61a8bdcad0a599b77d18bf1fe0404d8c'),
                ('*.p00', 715, '0465c30d0f958dd9b4dc3a29cf984799'),
                ('*.pal', 48, None),
                ('*.pt0', 5120, '32ca18808933aa12e979375d07048a11'),
                ('*.pt1', 578, '86c94775bdc63a9581e975d11568b87d'),
                ('*.pt2', 1250, '393017b9101a884b66d64849d99a7d05'),
                ('*.pt3', 3200, '9f0adfdbe740cb9cd8188a35761e2476'),
                ('*.pt4', 1600, '6ad00f47d8ad4f12005b22b2caa48f78'),
                ('*.pt5', 576, '36ab5bbc84127288a4bfbab259005f93'),
                ('*.pt6', 3750, '23cba673b42651247a9430c2bd288d5a'),
                ('*.pt7', 2048, 'b24b3c8abb318f365cd7b17ad91f1e30'),
                ('*.pt8', 1250, '393017b9101a884b66d64849d99a7d05'),
                ('*.say', 824, '54695fe2193256227f22054a88c06882'),
                ('*.sho', 40, 'fd4b38e94292e00251b9f39c47ee5710'),
                ('*.sng', 400, '12d329b5939034e95b42bff9b97b3d01'),
                ('*.stf', 84, '4a3a956ec0e1639fe3a54160809340bd'),
                ('*.stt', (3341, 30000), None),
                ('*.t00', (715, 1024), None),
                ('*.tap', 80, 'bbf7c6077962a7c28114dbd10be947cd'),
                ('*.til', 64000, 'cf7cf997851fba0edbb0524841ce37bd'),
                ('*.tmn', 210, '78d9c664c638a1d59b95c322a29da3f9'),
                ('*.veh', 240, None),
                ('*.z00', (257, 300), None),
                )
# XXX this class would complete testing a lot faster if these were executed exactly once,
# instead of once per method.    
    def setUp(self):
        self.name = temp()
        self.create(self.name)
        
    def tearDown(self):
        rm_rpgdir (self.name)
        
    def testRPGExists(self):
        """create(rpg) -> rpg exists"""
        ok(self.name).exists()
        ok(self.name).is_dir()
        
    def testDontOverwriteExistingRPG(self):
        """create(existing_dir) raises OSError"""
        name = temp()
        os.mkdir(name)
        ok(lambda: self.create(name)).raises(OSError)
        
    def testEnoughFiles(self):
        """create(rpg) -> 58+ files"""
        import glob
        ok (len (glob.glob (os.path.join (self.name,'*')))) >= 58

    def testEnoughData(self):
        """create(rpg) -> 230k+ of data"""
        import glob
        ok (sum (os.path.getsize(v) for v in glob.glob (os.path.join (self.name,'*')))) > (230 * 1024)

    def testExpectedLumps(self):
        """create(rpg) creates the expected lumps"""
        import glob
        for filename, expected_size, expected_sum in self.expected:
            resolved_filename = os.path.join(self.name, filename)
            if '*' in filename:
                matches = glob.glob(resolved_filename)
                ok(matches).length(1)
                resolved_filename = matches[0]
            else:
                ok(resolved_filename).exists()
                
            filesize = os.path.getsize(resolved_filename)
            if type(expected_size) == int:
                ok(filesize) == expected_size
            else:
                low, high = expected_size
                ok(filesize) <= high
                ok(filesize) >= low
            if expected_sum:
                actual_sum = md5(resolved_filename)
                ok(actual_sum) == expected_sum

    def testCreator(self):
        """archinym.lmp includes correct creator string"""
        with open(os.path.join(self.name, 'archinym.lmp'),'r') as f:
            prefix,creator = f.read().rstrip().split('\n')
            ok('nohrio').in_(creator)
    
    def testPrefix(self):
        """archinym.lmp includes correct prefix, and prefix of prefixed files matches."""
        import glob
        with open(os.path.join(self.name, 'archinym.lmp'),'r') as f:
            prefix, creator = f.read().rstrip().split('\n')
            ok(prefix) == os.path.basename(self.name)
            for filename, __, __ in self.expected:
                ok(glob.glob(os.path.join(self.name, filename))).length(1)

class CreateFromLumpedTest(TestCase):
    create = rpg_creator(template = 'ohrrpgce.new')
    def setUp(self):
        self.name = temp()
        self.create(self.name)
        
    def tearDown(self):
        rm_rpgdir (self.name)
        
    def testExpectedLumps(self):
        """create(rpg, template=LUMPED_RPG) creates the expected lumps"""
        import glob
        for filename, expected_size, expected_sum in CreateTest.expected:
            print ('checking %s' % filename) 
            resolved_filename = os.path.join(self.name, filename)
            if '*' in filename:
                matches = glob.glob(resolved_filename)
                ok(matches).length(1)
                resolved_filename = matches[0]
            else:
                ok(resolved_filename).exists()
                
            filesize = os.path.getsize(resolved_filename)
            if type(expected_size) == int:
                ok(filesize) == expected_size
            else:
                low, high = expected_size
                ok(filesize) <= high
                ok(filesize) >= low
            if expected_sum:
                actual_sum = md5(resolved_filename)
                ok(actual_sum) == expected_sum

    def testExpectedLumpsGZ(self):
        """create(rpg, template=LUMPED_RPG_GZ_FILEHANDLE) creates the expected lumps"""
        import gzip
        template = gzip.open('ohrrpgce.new.gz')
        creategz = rpg_creator (template = template)
        name = temp()
        creategz(name)
        import glob
        for filename, expected_size, expected_sum in CreateTest.expected:
            print ('checking %s' % filename) 
            resolved_filename = os.path.join(name, filename)
            if '*' in filename:
                matches = glob.glob(resolved_filename)
                ok(matches).length(1)
                resolved_filename = matches[0]
            else:
                ok(resolved_filename).exists()
                
            filesize = os.path.getsize(resolved_filename)
            if type(expected_size) == int:
                ok(filesize) == expected_size
            else:
                low, high = expected_size
                ok(filesize) <= high
                ok(filesize) >= low
            if expected_sum:
                actual_sum = md5(resolved_filename)
                ok(actual_sum) == expected_sum
        rm_rpgdir (name)

class CreateCustomizedTest(TestCase):
    create = rpg_creator(template = 'ohrrpgce.rpgdir')
    def test(self):
        """create(..., **kwargs) correctly applies kwargs to gen and archinym.lmp"""
        name = temp()
        self.create(name, creator = 'MagicalMuffinManufacturer 0.3 [via %s]', titlebg=2)
        with open(os.path.join (name, os.path.basename(name + '.gen')),'rb') as f:
            #titlebg is the second int16 in the file, after the 7-byte bload header.
            f.seek(7+2)
            import struct
            titlebg_now = struct.unpack('h', f.read(2))[0]
            ok(titlebg_now) == 2
        rm_rpgdir(name)
        

#class TMPLTest(TestCase):

#class TMPLTest(TestCase):
if __name__ == '__main__':
    #CreateTest.create = rpg_creator(template = 'ohrrpgce.new')
    nose.main(defaultTest='test_2create_and_verify.py')
    import glob
    for dirname in glob.glob('/tmp/nohrio*'):
        if not os.path.isdir(dirname):
            continue
        rm_rpgdir(dirname)