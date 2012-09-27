#!/usr/bin/env python3
#coding=utf8
"""Actual use cases for nohrio.

For these tests, usually completion means success.

Note that none of these tests actually complete yet.
That's dependent on the API I'm designing here being actually implemented :)
"""

from unittest import TestCase
import nose
from oktest import ok
import nohrio.nohrio2 as nohrio
import os
import numpy as np

#Filled in later, just before nose kicks in.
rpg = None

# This one will actually just about complete. We just gotta get to having a rpg object in the first place :)
def testCheckPassword():
    """Check whether a password is present.
    If it is, prompt the user to input the correct password in the terminal.
    """
    if rpg.gen.passinfo.present:
        input_pwd = input('Type password > ')
        rpg.gen.passinfo.check(input_pwd)

# and this one too
def testUpgradePassword():
    from nohrio.dtypes.general import LATEST_PASSWORD_FORMAT
    if rpg.gen.passinfo.present and rpg.gen.passinfo.version < LATEST_PASSWORD_FORMAT:
        if rpg.gen.passinfo.version == 4:
            # this is obviously insecure, it needs starring-out.
            input_pwd = input('Type password again > ')
        else:
            input_pwd = rpg.gen.passinfo.get()
        rpg.gen.passinfo.set(input_pwd, version=LATEST_PASSWORD_FORMAT)
        rpg.save(rpg.gen)

def testCheckMaxes():
    """Check gen.max fields conform with rpg managers' size"""
    maxes = gen.max
    tocheck = (v for v in dir(maxes) if isinstance(getattr(maxes, v), int) and (not v.startswith('_')))
    for name in tocheck:
        expected = getattr(maxes, v) + 1
        mgr = rpg.manager_by_name(name)
        nrecords = mgr.size
        if not (nrecords == expected):
            print ('Gen vs lump mismatch! Gen says %d records, lump has %d' % (expected, nrecords))

def testAddRecords():
    """Add some empty records to vehicle and attack lumps"""
    vehmax = rpg.max.vehicle
    attackmax = rpg.max.attack
    rpg.vehicles.append(None)
    rpg.vehicles.append(None)
    rpg.attacks.append(None)
    rpg.attacks.append(None)
    rpg.attacks.append(None)
    rpg.update_max('vehicle')
    rpg.update_max('attack')
    ok(rpg.max.vehicle) == (vehmax + 2)
    ok(rpg.max.attack) == (attackmax + 2)

def testDelRecord():
    """Delete a record from vehicle lump"""
    vehmax = rpg.max.vehicle
    attackmax = rpg.max.attack
    rpg.vehicles.remove_last()
    rpg.update_max('vehicle')
    ok(rpg.max.vehicle) == (vehmax - 1)

def testGetSprites():
    """Get a few hero sprites from rpg with default palettes."""
    # get a sequence of all 8 frames.
    heroa_gfx = rpg.gfx.hero.unpacked[0]
    herob_gfx = rpg.gfx.hero.unpacked[1]

def testRichData():
    """Access hero sprites and palette from hero data"""
    heroa = rpg.heros[0]
    herob = rpg.heros[1]
    # XXX needs some thought. appearance in a sub-structure eg. heroa.vis.palette?
    apal_id = heroa.palette
    bframes_id = herob.frames
    # current version of the 'richdata' idea.
    apal_data = heroa.palette()
    bframes_data = herob.frames()

#slow
def testPaletteUsage():
    """For each 16-color palette, collect usage statistics."""
    #
    #
    npalettes = len(rpg.palettes)
    usage = np.zeros(npalettes, 'u4')

    # rpg.resolvepal looks at palette._defpalindex
    # (to be more precise, palette.__class__._defpalindex)
    # to get the index of the defpalX.bin file to lookup the default in.
    #
    # We have a subclass of PaletteId for each n in PT[0-8];
    # all they do is set cls._defpalindex appropriately.
    #
    # Incidentally, what does PT mean anyway? Is it a reference to QBasic PUT?



    # Bound methods are interesting:
    resolvepal = rpg.resolvepal

    for user in rpg.heros:
        palette = resolvepal(user.palette)
        usage[palette] += 1

    for users in (rpg.enemies, rpg.attacks, rpg.items):
        for user in users:
            palette = resolvepal(user.palette)
            usage[palette] += 1

    for user in rpg.textboxes:
        if user.portrait.type != 'fixed':
            continue
        palette = resolvepal(user.portrait.palette)
        usage[palette] += 1

    for map in rpg.maps:
        for user in map.npcdefs:
            palette = resolvepal(user.palette)
            usage[palette] += 1
    # what else?

    #summarize:
    totaluses = sum(usage)
    indices = np.argsort(mostused)
    topi = indices[:0x10]
    print ('There were %d palette uses in total' % totaluses)
    print ('Top 0x10 in usage:')
    for index in topi:
        print ('\t%d\t%6d uses' % (index, usage[index]))


def test_formationUsage():
    """List formations and formationsets that are not used."""
    nformations = len(rpg.formation)
    nformsets = len(rpg.formset)
    allformsets = list(range(nformsets))
    allforms = list(range(nformations))
    unusedfsets = set(allformsets)
    unusedforms = set(allforms)

    for map in rpg.maps:
        foemap = map.foemap
        for used in np.unique(foemap):
            unusedformsets.discard(used)
    for i, formset in enumerate(rpg.formset):
        if i in unusedfsets:
            # since the fset isn't used, the formations
            # it uses don't qualify as used either.
            continue
        for used in formset.entries:
            used -= 1
            if used == 0:
                continue
            unusedforms.discard(used)
    unusedfsets = sorted(unusedfsets)
    unusedforms = sorted(unusedforms)
    print ("Unused formationsets: ", ' '.join(str(v) for v in unusedfsets))
    print ("Unused formations: ", ' '.join(str(v) for v in unusedforms))

if __name__ == "__main__":
    # setup stuff here:
    #   * copy the vikings.rpgdir into a sandbox.rpgdir
    #
    # rpg = nohrio.rpg(sandbox)
    #
    nose.main(defaultTest='test_usecases.py')
