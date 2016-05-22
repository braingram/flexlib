#!/usr/bin/env python

#Flexlib/API.cs:34
FLEX_OUI = 0x1C2D

#Vita/VitaFlex.cs
VF_DISCOVERY = 0xFFFF
VF_METER = 0x8002
VF_WATERFALL = 0x8004
VF_OPUS = 0x8005
VF_IF_NARROW = 0x03E3
VF_WIDE_24 = 0x02E3
VF_WIDE_48 = 0x02E4
VF_WIDE_96 = 0x02E5
VF_WIDE_192 = 0x02E6

#Vita/VitaCommon.cs:29
PT_IF = 0
PT_IF_STREAM = 1
PT_EXT = 2
PT_EXT_STREAM = 3

#Vita/VitaCommon.cs:42
TSI_NONE = 0
TSI_UTC = 1
TSI_GPS = 2
TSI_OTHER = 3

#Vita/VitaCommon.cs:53
TSF_NONE = 0
TSF_SAMPLE = 1  # sample count
TSF_RT = 2  # realtime, picoseconds
TSF_FREE = 3  # free running
