# Module for reading Global Text Strings from an .STT lump.
# Unlike the .stt support in ohrrpgce.py, this can be easily
# kept upt to date.

import numpy as np

stt_offsets = []

def add_item(index, *args):
    stt_offsets.append(index)

add_item(0,   "Health Points",              "HP", 10)
add_item(1,   "Spell Points",               "MP", 10)
add_item(2,   "Attack Power",               "Atk", 10)
add_item(3,   "Accuracy",                   "Aim", 10)
add_item(4,   "Extra Hits number",          "Hits", 10)
add_item(5,   "Defense/Blocking Power",     "Def", 10)
add_item(6,   "Dodge",                      "Dodge", 10)
add_item(7,   "Unused stat (aka Counter)",  "Ctr", 10)
add_item(8,   "Speed",                      "Speed", 10)
add_item(29,  "Spell Skill",                "Magic", 10)
add_item(30,  "Spell Defense",              "Will", 10)
add_item(31,  "Spell Cost Reduction %",     "MP~", 10)
for i in range(64):
    add_item(174 + i*2, "Elemental " + str(i),     "element", 14)
add_item(38,  "Weapon",                     "Weapon", 10)
add_item(25,  "Armor 1",                    "Head", 10)
add_item(26,  "Armor 2",                    "Body", 10)
add_item(27,  "Armor 3",                    "Arms", 10)
add_item(28,  "Armor 4",                    "Legs", 10)
add_item(60,  "Items",                      "Items", 10)
add_item(61,  "Spells",                     "Spells", 10)
add_item(62,  "Status",                     "Status", 10)
add_item(63,  "Equip",                      "Equip", 10)
add_item(64,  "Order",                      "Order", 10)
add_item(65,  "Team",                       "Team", 10)
add_item(66,  "Save",                       "Save", 10)
add_item(322, "Load",                       "Load", 20)
add_item(67,  "Quit",                       "Quit", 10)
add_item(68,  "Minimap",                    "Map", 10)
add_item(69,  "Volume Menu [obsolete]",     "Volume", 10)
add_item(318, "Music Volume",               "Music", 20)
add_item(320, "Sound Volume",               "Sound", 20)
add_item(308, "TV Margins [consoles only]", "Margins", 10)
add_item(313, "In-App Purchases",           "Purchases", 10)
add_item(314, "Switch to windowed",         "Windowed", 20)
add_item(316, "Switch to fullscreen",       "Fullscreen", 20)
add_item(35,  "Exit Item Menu",             "DONE", 10)
add_item(36,  "Sort Item Menu",             "AUTOSORT", 10)
add_item(37,  "Drop Item",                  "TRASH", 10)
add_item(41,  "Drop Prompt",                "Discard", 10)
add_item(42,  "Negative Drop Prefix",       "Cannot", 10)
add_item(43,  "Level",                      "Level", 10)
add_item(33,  "Experience",                 "Experience", 10)
add_item(47,  "(exp) for next (level)",     "for next", 10)
add_item(330, "Money/Price",                "$#", 16, "money")
add_item(160, "Level MP",                   "Level MP", 20)
add_item(302, "Elemental Effects Title",    "Elemental Effects:", 30)
add_item(130, "No Elemental Effects",       "No Elemental Effects", 30)
add_item(162, "Takes > 100% element dmg",   "Weak to $E", 30,   "elemental_resist")
add_item(165, "Takes 0 to 100% element dmg","Strong to $E", 30, "elemental_resist")
add_item(168, "Takes 0% element dmg",       "Immune to $E", 30, "elemental_resist")
add_item(171, "Takes < 0% element dmg",     "Absorb $E", 30,   "elemental_resist")
add_item(110, "Equip Nothing (unequip)",    "Nothing", 10)
add_item(39,  "Unequip All",                "-REMOVE-", 8)
add_item(40,  "Exit Equip",                 "-EXIT-", 8)
add_item(133, "(hero) has no spells",       "has no spells", 20)
add_item(46,  "Exit Spell List Menu",       "EXIT", 10)
add_item(51,  "Cancel Spell Menu",          "(CANCEL)", 10)
add_item(48,  "Remove Hero from Team",      "REMOVE", 10)
add_item(52,  "New Game",                   "NEW GAME", 10)
add_item(53,  "Exit Game",                  "EXIT", 10)
add_item(59,  "Cancel Save",                "CANCEL", 10)
add_item(102, "Replace Save Prompt",        "Replace Old Data?", 20)
add_item(44,  "Overwrite Save Yes",         "Yes", 10)
add_item(45,  "Overwrite Save No",          "No", 10)
add_item(154, "day",                        "day", 10)
add_item(155, "days",                       "days", 10)
add_item(156, "hour",                       "hour", 10)
add_item(157, "hours",                      "hours", 10)
add_item(158, "minute",                     "minute", 10)
add_item(159, "minutes",                    "minutes", 10)
add_item(55,  "Prompt",                     "Quit Playing?", 20)
add_item(57,  "Yes",                        "Yes", 10)
add_item(58,  "No",                         "No", 10)
add_item(70,  "Buy",                        "Buy", 10)
add_item(71,  "Sell",                       "Sell", 10)
add_item(72,  "Inn",                        "Inn", 10)
add_item(73,  "Hire",                       "Hire", 10)
add_item(74,  "Exit",                       "Exit", 10)
add_item(324, "You own (itemcount)",        "You own", 20)
add_item(326, "Equipped (itemcount)",       "Equipped", 20)
add_item(85,  "Trade for (items, no $)",    "Trade for", 20, "trade_for_prefix")
add_item(328, "Trade-in amount you have",   " (have $N)", 20, "trade_item_owned")
add_item(87,  "Hire price prefix",          "Joins for", 20)
add_item(97,  "(#) in stock",               "in stock", 20)
add_item(99,  "Equipability prefix",        "Equip:", 10)
add_item(89,  "Cannot buy prefix",          "Cannot Afford", 20)
add_item(91,  "Cannot hire prefix",         "Cannot Hire", 20)
add_item(305, "Inventory full warning",     "No room in inventory", 30)
add_item(100, "Party full warning",         "No room in party", 20)
add_item(93,  "Buy alert",                  "Purchased", 20)
add_item(95,  "Hire alert (suffix)",        "Joined!", 20)
add_item(309, "The shop is empty",          "The shop is empty", 30)
add_item(77,  "Value: Worth ($) (and...)",  "Worth", 20)
add_item(81,  "($) and a (item)",           "and a", 10)
add_item(153, "($) and (number) (item)",    "and", 10)
add_item(79,  "Value: Trade for (item)",    "Trade for", 20)
add_item(82,  "Worthless item warning",     "Worth Nothing", 20)
add_item(75,  "Unsellable item warning",    "CANNOT SELL", 20)
add_item(84,  "Sell alert",                 "Sold", 10)
add_item(143, "THE INN COSTS ($)",          "THE INN COSTS", 20)
add_item(145, "You have ($)",               "You have", 20)
add_item(49,  "Pay at Inn",                 "Pay", 10)
add_item(50,  "Cancel Inn",                 "Cancel", 10)
add_item(34,  "Battle Item Menu",           "Item", 10)
add_item(117, "Stole (itemname)",           "Stole", 30)
add_item(111, "Nothing to Steal",           "Has Nothing", 30)
add_item(114, "Steal Failure",              "Cannot Steal", 30)
add_item(120, "When an Attack Misses",      "miss", 20)
add_item(122, "When a Spell Fails",         "fail", 20)
add_item(147, "CANNOT RUN!",                "CANNOT RUN!", 20)
add_item(54,  "Pause",                      "PAUSE", 10)
add_item(126, "Gained (experience)",        "Gained", 10)
add_item(149, "Level up for (hero)",        "Level up for", 20)
add_item(151, "(#) levels for (hero)",      "levels for", 20)
add_item(124, "(hero) learned (spell)",     "learned", 10)
add_item(139, "Found a (item)",             "Found a", 20)
add_item(141, "Found (number) (items)",     "Found", 20)
add_item(125, "Found ($)",                  "Found", 10)
add_item(104, "Status Prompt",              "Whose Status?", 20)
add_item(106, "Spells Prompt",              "Whose Spells?", 20)
add_item(108, "Equip Prompt",               "Equip Who?", 20)
add_item(135, "Plotscript: pick hero",      "Which Hero?", 20)
add_item(137, "Hero name prompt",           "Name the Hero", 20)

stt_offsets.sort()


def stt_strings(rpg):
    "Return an offset -> string mapping and a list of errors, given an RPGHandler"
    lumpsize = rpg.lump_size('stt')
    if lumpsize == 0:
        return {}, ["No/zero-length .stt lump"]
    dtype = np.dtype([('data', np.uint8, lumpsize)])
    lump = rpg.flexidata('stt', dtype=dtype)
    #lump = lump.view(np.dtype([('data', np.uint8, len(lump))]))
    lump = lump[0]['data']

    ret = {}
    invalid = []
    for offset in stt_offsets:
        off = offset * 11
        if off < len(lump):
            length = lump[off]
            if length > 30:
                invalid.append("String %d: Invalid length %d" % (offset, length))
            elif length == 0:
                ret[offset] = ""
            else:
                text = lump[off+1:off+length+1].view(np.dtype('S%d' % length))[0]
                ret[offset] = text
    return ret, invalid
