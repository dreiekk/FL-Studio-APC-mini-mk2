#name=AKAI APC mini MKii (Performance Mode)

#
# Akai APC mini Mk2 - Communication Protocol PDF
#
# https://cdn.inmusicbrands.com/akai/attachments/APC%20mini%20mk2%20-%20Communication%20Protocol%20-%20v1.0.pdf
#

#
# (unofficial) FL Studio Python API Reference
#
# https://miguelguthridge.github.io/FL-Studio-API-Stubs/
#

#
# List of Script Events (On... Functions)
#
# https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/midi_scripting.htm#script_events
#

import math

import midi
import device
import playlist
import transport
import utils


def OnInit():
    clearLights()
    updateLights()


def OnDeInit():
    clearLights()


zone_offset_x = 0
zone_offset_y = 0

def OnNoteOn(event):
    global zone_offset_x
    global zone_offset_y

    event.handled = True
    print('Midi note on:', event.data1, " ", event.data2)

    flag = 1 # trigger schedule ?
    if transport.isPlaying():
        flag = 2 # trigger now ?

    if (event.data1 <= 63):
        print('Note Location: Grid Pad')
        trackIndexBottomUpZeroSeven = (math.ceil((event.data1 + 1) / 8) - 1)

        trackIndex = (8 - trackIndexBottomUpZeroSeven) + zone_offset_y
        blockNum = (event.data1 - (trackIndexBottomUpZeroSeven * 8)) + zone_offset_x

        print ('triggering track:', trackIndex, ' block:', blockNum)

        playlist.triggerLiveClip(trackIndex, blockNum, flag, -1)
        playlist.refreshLiveClips()

    if event.data1 == 100:
        if transport.isPlaying():
            transport.stop()
        else:
            transport.start()

    if event.data1 >= 104 and event.data1 <= 107:
        if event.data1 == 104 and zone_offset_y > 0:
            zone_offset_y -= 1
        if event.data1 == 105:
            zone_offset_y += 1
        if event.data1 == 106 and zone_offset_x > 0:
            zone_offset_x -= 1
        if event.data1 == 107:
            zone_offset_x += 1

        print('New Zone Offsets: ', zone_offset_x, zone_offset_y)

        playlist.liveDisplayZone(0 + zone_offset_x, 1 + zone_offset_y, 8 + zone_offset_x, 9 + zone_offset_y)

    if event.data1 >= 112 and event.data1 <= 119:

        trackIndex = event.data1 - (112 - 1)

        print('Muting track: ', trackIndex)

        playlist.triggerLiveClip(trackIndex, -1, flag)
        playlist.refreshLiveClips()

    updateLights()


def OnNoteOff(event):
    event.handled = True


def clearLights(onlypad=False):
    for i in range(0, 64):
        device.midiOutMsg(0x90 + (i << 8) + (0x00 << 16))
    
    if (onlypad == False):
        for i in range (0x64, 0x78):
            device.midiOutMsg(0x90 + (i << 8) + (0 << 16))


def OnUpdateLiveMode(lastTrack):
    updateLights()


last_beat_val = 0
def OnUpdateBeatIndicator(value):
    global last_beat_val

    if (transport.isPlaying() == False):
        device.midiOutMsg(0x90 + (0x64 << 8) + (1 << 16))
        device.midiOutMsg(0x90 + (0x65 << 8) + (0 << 16))
        device.midiOutMsg(0x90 + (0x66 << 8) + (0 << 16))
        device.midiOutMsg(0x90 + (0x67 << 8) + (0 << 16))
        return

    last_beat_val += 1
    if (value == 1):
        last_beat_val = 1

    device.midiOutMsg(0x90 + (0x64 << 8) + ((1 if last_beat_val == 1 or last_beat_val == 2 else 0) << 16))
    device.midiOutMsg(0x90 + (0x65 << 8) + ((1 if last_beat_val == 3 or last_beat_val == 4 else 0) << 16))
    device.midiOutMsg(0x90 + (0x66 << 8) + ((1 if last_beat_val == 5 or last_beat_val == 6 else 0) << 16))
    device.midiOutMsg(0x90 + (0x67 << 8) + ((1 if last_beat_val == 7 or last_beat_val == 8 else 0) << 16))


def updateLights():
    global zone_offset_x
    global zone_offset_y

    is_playing = transport.isPlaying()

    for x in range(0, 8):
        for y in range (0, 8):
            midiNum = x + y * 8
            trackIndex = (8 - y) + zone_offset_y
            blockIndex = x + zone_offset_x

            result = playlist.getLiveBlockStatus(trackIndex, blockIndex, midi.LB_Status_Simple)
            # 0 = empty
            # 1 = filled
            # 2 = playing (or scheduled)
            # 3 = scheduled (and not playing)

            brightness = 0x96
            color = 0

            blockColor = playlist.getLiveBlockColor(trackIndex, blockIndex)

            # filled
            if result == 1:
                # color = 41 # cyan
                color = flColorHexToNearestApcIndex(blockColor)
                brightness = 0x91

            # playing
            if result == 2:
                color = 20 # green
                brightness = 0x96
                # brightness = 0x99

            # scheduled
            if result == 3:
                if is_playing == False:
                    color = 9 # orange
                else:
                    color = flColorHexToNearestApcIndex(blockColor)
                    brightness = 0x91

            sendLightMsg(midiNum, color, brightness)

    if (transport.isPlaying() == False):
        device.midiOutMsg(0x90 + (0x64 << 8) + (1 << 16))


def OnRefresh(flags):
    updateLights()


def sendLightMsg(buttonNum, color, brightness=0x96):
    device.midiOutMsg(brightness + (buttonNum << 8) + (color << 16))


APC_COLORS = (
    (0   , 0,    0,    0)  ,  #000000 
    (1   , 30,    30,    30)  ,  #1E1E1E 
    (2   , 127,    127,    127)  ,  #7F7F7F 
    (3   , 255,    255,    255)  ,  #FFFFFF 
    (4   , 255,    76,    76)  ,  #FF4C4C 
    (5   , 255,    0,    0)  ,  #FF0000 
    (6   , 89,    0,    0)  ,  #590000 
    (7   , 25,    0,    0)  ,  #190000 
    (8   , 255,    189,    108)  ,  #FFBD6C 
    (9   , 255,    84,    0)  ,  #FF5400 
    (10  , 89,    29,    0)  ,  #591D00 
    (11  , 39,    27,    0)  ,  #271B00 
    (12  , 255,    255,    76)  ,  #FFFF4C 
    (13  , 255,    255,    0)  ,  #FFFF00 
    (14  , 89,    89,    0)  ,  #595900 
    (15  , 25,    25,    0)  ,  #191900 
    (16  , 136,    255,    76)  ,  #88FF4C 
    (17  , 84,    255,    0)  ,  #54FF00 
    (18  , 29,    89,    0)  ,  #1D5900 
    (19  , 20,    43,    0)  ,  #142B00 
    (20  , 76,    255,    76)  ,  #4CFF4C 
    (42  , 0,    29,    89)  ,  #001D59 
    (43  , 0,    8,    25)  ,  #000819 
    (44  , 76,    76,    255)  ,  #4C4CFF 
    (45  , 0,    0,    255)  ,  #0000FF 
    (46  , 0,    0,    89)  ,  #000059 
    (47  , 0,    0,    25)  ,  #000019 
    (48  , 135,    76,    255)  ,  #874CFF 
    (49  , 84,    0,    255)  ,  #5400FF 
    (50  , 25,    0,    100)  ,  #190064 
    (51  , 15,    0,    48)  ,  #0F0030 
    (52  , 255,    76,    255)  ,  #FF4CFF 
    (53  , 255,    0,    255)  ,  #FF00FF 
    (54  , 89,    0,    89)  ,  #590059 
    (55  , 25,    0,    25)  ,  #190019 
    (56  , 255,    76,    135)  ,  #FF4C87 
    (57  , 255,    0,    84)  ,  #FF0054 
    (58  , 89,    0,    29)  ,  #59001D 
    (59  , 34,    0,    19)  ,  #220013 
    (60  , 255,    21,    0)  ,  #FF1500 
    (61  , 153,    53,    0)  ,  #993500 
    (62  , 121,    81,    0)  ,  #795100 
    (63  , 67,    100,    0)  ,  #436400 
    (64  , 3,    57,    0)  ,  #033900 
    (65  , 0,    87,    53)  ,  #005735 
    (66  , 0,    84,    127)  ,  #00547F 
    (67  , 0,    0,    255)  ,  #0000FF 
    (68  , 0,    69,    79)  ,  #00454F 
    (69  , 37,    0,    204)  ,  #2500CC 
    (70  , 127,    127,    127)  ,  #7F7F7F 
    (71  , 32,    32,    32)  ,  #202020 
    (42  , 0,    29,    89)  ,  #001D59 
    (43  , 0,    8,    25)  ,  #000819 
    (44  , 76,    76,    255)  ,  #4C4CFF 
    (45  , 0,    0,    255)  ,  #0000FF 
    (46  , 0,    0,    89)  ,  #000059 
    (47  , 0,    0,    25)  ,  #000019 
    (48  , 135,    76,    255)  ,  #874CFF 
    (49  , 84,    0,    255)  ,  #5400FF 
    (50  , 25,    0,    100)  ,  #190064 
    (51  , 15,    0,    48)  ,  #0F0030 
    (52  , 255,    76,    255)  ,  #FF4CFF 
    (53  , 255,    0,    255)  ,  #FF00FF 
    (54  , 89,    0,    89)  ,  #590059 
    (55  , 25,    0,    25)  ,  #190019 
    (56  , 255,    76,    135)  ,  #FF4C87 
    (57  , 255,    0,    84)  ,  #FF0054 
    (58  , 89,    0,    29)  ,  #59001D 
    (59  , 34,    0,    19)  ,  #220013 
    (60  , 255,    21,    0)  ,  #FF1500 
    (61  , 153,    53,    0)  ,  #993500 
    (62  , 121,    81,    0)  ,  #795100 
    (21  , 0,    255,    0)  ,  #00FF00 
    (22  , 0,    89,    0)  ,  #005900 
    (23  , 0,    25,    0)  ,  #001900 
    (24  , 76,    255,    94)  ,  #4CFF5E 
    (25  , 0,    255,    25)  ,  #00FF19 
    (26  , 0,    89,    13)  ,  #00590D 
    (27  , 0,    25,    2)  ,  #001902 
    (28  , 76,    255,    136)  ,  #4CFF88 
    (29  , 0,    255,    85)  ,  #00FF55 
    (30  , 0,    89,    29)  ,  #00591D 
    (31  , 0,    31,    18)  ,  #001F12 
    (32  , 76,    255,    183)  ,  #4CFFB7 
    (33  , 0,    255,    153)  ,  #00FF99 
    (34  , 0,    89,    53)  ,  #005935 
    (35  , 0,    25,    18)  ,  #001912 
    (36  , 76,    195,    255)  ,  #4CC3FF 
    (37  , 0,    169,    255)  ,  #00A9FF 
    (38  , 0,    65,    82)  ,  #004152 
    (39  , 0,    16,    25)  ,  #001019 
    (40  , 76,    136,    255)  ,  #4C88FF 
    (41  , 0,    85,    255)  ,  #0055FF 
    (72  , 255,    0,    0)  ,  #FF0000 
    (73  , 189,    255,    45)  ,  #BDFF2D 
    (74  , 175,    237,    6)  ,  #AFED06 
    (75  , 100,    255,    9)  ,  #64FF09 
    (76  , 16,    139,    0)  ,  #108B00 
    (77  , 0,    255,    135)  ,  #00FF87 
    (78  , 0,    169,    255)  ,  #00A9FF 
    (79  , 0,    42,    255)  ,  #002AFF 
    (80  , 63,    0,    255)  ,  #3F00FF 
    (81  , 122,    0,    255)  ,  #7A00FF 
    (82  , 178,    26,    125)  ,  #B21A7D 
    (83  , 64,    33,    0)  ,  #402100 
    (84  , 255,    74,    0)  ,  #FF4A00 
    (85  , 136,    225,    6)  ,  #88E106 
    (86  , 114,    255,    21)  ,  #72FF15 
    (87  , 0,    255,    0)  ,  #00FF00 
    (88  , 59,    255,    38)  ,  #3BFF26 
    (89  , 89,    255,    113)  ,  #59FF71 
    (90  , 56,    255,    204)  ,  #38FFCC 
    (91  , 91,    138,    255)  ,  #5B8AFF 
    (92  , 49,    81,    198)  ,  #3151C6 
    (93  , 135,    127,    233)  ,  #877FE9 
    (94  , 211,    29,    255)  ,  #D31DFF 
    (95  , 255,    0,    93)  ,  #FF005D 
    (96  , 255,    127,    0)  ,  #FF7F00 
    (97  , 185,    176,    0)  ,  #B9B000 
    (98  , 144,    255,    0)  ,  #90FF00 
    (99  , 131,    93,    7)  ,  #835D07 
    (100 , 57,    43,    0)  ,  #392b00 
    (101 , 20,    76,    16)  ,  #144C10 
    (102 , 13,    80,    56)  ,  #0D5038 
    (103 , 21,    21,    42)  ,  #15152A 
    (104 , 22,    32,    90)  ,  #16205A 
    (105 , 105,    60,    28)  ,  #693C1C 
    (106 , 168,    0,    10)  ,  #A8000A 
    (107 , 222,    81,    61)  ,  #DE513D 
    (108 , 216,    106,    28)  ,  #D86A1C 
    (109 , 255,    225,    38)  ,  #FFE126 
    (110 , 158,    225,    47)  ,  #9EE12F 
    (111 , 103,    181,    15)  ,  #67B50F 
    (112 , 30,    30,    48)  ,  #1E1E30 
    (113 , 220,    255,    107)  ,  #DCFF6B 
    (114 , 128,    255,    189)  ,  #80FFBD 
    (115 , 154,    153,    255)  ,  #9A99FF 
    (116 , 142,    102,    255)  ,  #8E66FF 
    (117 , 64,    64,    64)  ,  #404040 
    (118 , 117,    117,    117)  ,  #757575 
    (119 , 224,    255,    255)  ,  #E0FFFF 
    (120 , 160,    0,    0)  ,  #A00000 
    (121 , 53,    0,    0)  ,  #350000 
    (122 , 26,    208,    0)  ,  #1AD000 
    (123 , 7,    66,    0)  ,  #074200 
    (124 , 185,    176,    0)  ,  #B9B000 
    (125 , 63,    49,    0)  ,  #3F3100 
    (126 , 179,    95,    0)  ,  #B35F00 
    (127 , 75,    21,    2)  ,  #4B1502 
)


def closestApcColor(rgb):
    r, g, b = rgb
    color_diffs = []
    for color in APC_COLORS:
        index, cr, cg, cb = color
        color_diff = math.sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
        color_diffs.append((color_diff, color))
    return min(color_diffs)[1]


def flColorHexToNearestApcIndex(colorHex):
    fl_rgb = utils.ColorToRGB(colorHex)
    apc_rgb = closestApcColor(fl_rgb)
    return apc_rgb[0] # index of APC_COLOR
