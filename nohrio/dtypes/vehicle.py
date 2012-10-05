from nohrio.basedtypes import *
from bits import mkenum, MultiRange

# XXX the main class definition is out of date , it needs new api seriously.

OverrideWalls = mkenum('OverrideWalls',
                       {0: 'default',
                        1: 'vehicle A',
                        2: 'vehicle B',
                        3: 'vehicle A and B',
                        4: 'vehicle A or B',
                        5: 'not vehicle A',
                        6: 'not vehicle B',
                        7: 'not (vehicle A or B)',
                        8: 'everywhere'},
                        MultiRange(((0,8))))

SPEED_ENUM = (0,1,2,10,4,5)

BITSETS = ('pass_walls',
           'pass_npcs',
           'activatable_npcs',
           'usable_doors',
           'no_hideleader',
           'no_hideparty',
           'dismount_1space_ahead',
           'dismount_pass_walls',
           'no_flying_shadow',
           'UNUSED9',
           'UNUSED10',
           'UNUSED11',
           'UNUSED12',
           'UNUSED13',
           'UNUSED14',
           'UNUSED15',
           'UNUSED16',
           'UNUSED17',
           'UNUSED18',
           'UNUSED19',
           'UNUSED20',
           'UNUSED21',
           'UNUSED22',
           'UNUSED23',
           'UNUSED24',
           'UNUSED25',
           'UNUSED26',
           'UNUSED27',
           'UNUSED28',
           'UNUSED29',
           'UNUSED30',
           'UNUSED31')

DTYPE = DType ("""<16B:name: h:speed: 2B:bitsets: h:randbattles:
                  h:usebutton: h:menubutton: h:ridingtag:
                  h:onmount: h:ondismount:
                  h:overridewalls: h:blockedby:
                  h:mountfrom: h:dismount_to:
                  h:elevation: 18h:reserved:""").freeze()

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

RandomBattles = mkenum('RandomBattles',
                       {-1: 'disabled',
                         0: 'enabled',},
                        valid=MultiRange(((-1, INT16_MAX),)),
                        format=lambda self: 'formation set %d' % int(self))

ButtonEffect = mkenum('ButtonEffect',
                      {-2: 'disabled',
                       -1: 'enabled',
                        0: 'dismount'}
                      valid=MultiRange(((-2, INT16_MAX),))
                      format=lambda self: 'run plotscript %d' % int(self))

# ohrstring 'format' kwarg: length-2 string
TagSet = ohrtype (enum = [[[None, -1], lambda v:'Set tag %d OFF' % abs(v)],
                          [0,'N/A'],
                          [[1, None], 'Set tag {value} ON']])
TriggerOrTextbox = mkenum('TriggerOrTextbox',
                          {0: 'N/A'},
                          valid = MultiRange(((-(INT16_MAX - 1), INT16_MAX))),
                          format=lambda self: ('plotscript trigger %d'
                                                if int(v) < 0 else
                                                'textbox %d') % abs(self))

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

