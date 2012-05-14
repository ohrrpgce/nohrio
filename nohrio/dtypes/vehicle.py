# Planning
# there are two types of file structure, those that require parsing and those that don't.
# We use LEPL's binary support for the one, and NumPy for the other.
from nohrio.basedtypes import *




Speed = positive*ohrtype (enum=(0,1,2,10,4,5))
VehicleBitsets = bitsets ('dismount_passes_walls,Pass walls while dismounting',
                          'dismount_ahead,Dismount one space ahead',
                          'no_hideparty,Don\'t hide party',
                          'no_hideleader,Don\'t hide leader',
                          'doors_usable,Enable door use',
                          'npcs_activatable,Enable NPC activation',
                          'passthru_npcs,Pass through NPCs',
                          'passthru_walls,Pass through walls',
                          '?7',
                          'no_flying_shadow,Disable flying shadow',
                          '?16')
RandomBattles = ohrtype (enum = [[-1, 'Disabled'],
                               [0, 'Enabled'],
                               [[1, None], 'Formation set {value}']])
ButtonEffect = ohrtype (enum = [[-2, 'Disabled'],[-1, 'Menu'],[0, 'Dismount'],[[1, None], 'Run plotscript {value}']])
# ohrstring 'format' kwarg: length-2 string
TagSet = ohrtype (enum = [[[None, -1], lambda v:'Set tag %d OFF' % abs(v)],
                          [0,'N/A'],
                          [[1, None], 'Set tag {value} ON']])
TriggerOrTextbox = ohrtype (enum = [[[None, -1], lambda v:'Plotscript trigger %d' % abs(v)],
                                    [0, 'N/A'],
                                    [[1, None], 'Textbox {value}']])
VehicleWallHandling = ohrtype (enum = 'Default,Vehicle A,Vehicle B,Vehicle A+B,Vehicle A or B,Not vehicle A,'
                                      'Not vehicle B,Neither A nor B,Everywhere')

# if need be, we could specify custom validation using a 'validate' kwarg

class Vehicle(adtype, groups={'button':'usebutton menubutton',
                               'wallhandling':'overridewalls blockedby mountfrom dismountto',
                               'appearance':'speed elevation bitsets'}):
    name = ohrstring (15, format='cc')
    speed = Speed ('Raw speed')
    bitsets = VehicleBitsets ()
    randombattles = RandomBattles ('Random battle behaviour while riding this vehicle')
    usebutton = ButtonEffect ('Effect when "use" button is pressed')
    menubutton = ButtonEffect ('Effect when "menu" button is pressed')
    settag = TagSet ('Set tag when using this vehicle')
    onmount = TriggerOrTextbox ('Effect when mounting')
    ondismount = TriggerOrTextbox ('Effect when dismounting')
    overridewalls = VehicleWallHandling ()
    blockedby = VehicleWallHandling ('Blocked by')
    mountfrom = VehicleWallHandling ('Mount from')
    dismountto = VehicleWallHandling ('Dismount to')
    elevation = INT('Elevation in pixels')
    unused = 18 * INT
    EXPECTEDSIZE = 80

