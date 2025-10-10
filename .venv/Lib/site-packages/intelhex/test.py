# Copyright (c) 2005-2018, Alexander Belchenko
# All rights reserved.
#
# Redistribution and use in source and binary forms,
# with or without modification, are permitted provided
# that the following conditions are met:
#
# * Redistributions of source code must retain
#   the above copyright notice, this list of conditions
#   and the following disclaimer.
# * Redistributions in binary form must reproduce
#   the above copyright notice, this list of conditions
#   and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of the author nor the names
#   of its contributors may be used to endorse
#   or promote products derived from this software
#   without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Test suite for IntelHex library."""

import array
import os
import shlex
import subprocess
import sys
import tempfile
import unittest

import intelhex
from intelhex import (
    IntelHex,
    IntelHexError,
    HexReaderError,
    AddressOverlapError,
    HexRecordError,
    RecordLengthError,
    RecordTypeError,
    RecordChecksumError,
    EOFRecordError,
    ExtendedSegmentAddressRecordError,
    ExtendedLinearAddressRecordError,
    StartSegmentAddressRecordError,
    StartLinearAddressRecordError,
    DuplicateStartAddressRecordError,
    InvalidStartAddressValueError,
    _EndOfFile,
    BadAccess16bit,
    hex2bin,
    Record,
    )
from intelhex import compat
from intelhex.compat import (
    BytesIO,
    StringIO,
    UnicodeType,
    array_tobytes,
    asbytes,
    asstr,
    dict_items_g,
    range_g,
    range_l,
    )
from intelhex.__version__ import version_str

__docformat__ = 'restructuredtext'

##
# Data for tests

hex8 = '''\
:1004E300CFF0FBE2FDF220FF20F2E120E2FBE6F396
:1004F3000A00FDE0E1E2E3B4E4E5BAE6E7B3BFE80E
:10050300E9EAEBECEDEEEFF0F1F2F3F4F5F6F7F8E0
:10051300F9FCFEFF00C0C1C2C3A5C4C5AAC6C7B2C9
:10052300AFC8C9CACBCCCDCECFD0D1D2D3D4D5D6F8
:07053300D7D8D9DCDEDF00A0
:10053A0078227C007D007BFF7A0479F57E007F2398
:10054A0012042F78457C007D007BFF7A0579187E9E
:10055A00007F2212042F759850438920758DDDD2B1
:10056A008ED2996390017BFF7A0479E31200658049
:01057A00FE82
:030000000205A254
:0C05A200787FE4F6D8FD75817A02053AF6
:10035F00E709F608DFFA8046E709F208DFFA803E80
:10036F0088828C83E709F0A3DFFA8032E309F6086D
:10037F00DFFA8078E309F208DFFA807088828C83D5
:10038F00E309F0A3DFFA806489828A83E0A3F60889
:10039F00DFFA805889828A83E0A3F208DFFA804C63
:1003AF0080D280FA80C680D4806980F2803380103A
:1003BF0080A680EA809A80A880DA80E280CA8033A3
:1003CF0089828A83ECFAE493A3C8C582C8CCC5831B
:1003DF00CCF0A3C8C582C8CCC583CCDFE9DEE780EB
:1003EF000D89828A83E493A3F608DFF9ECFAA9F06A
:1003FF00EDFB2289828A83ECFAE0A3C8C582C8CCC0
:10040F00C583CCF0A3C8C582C8CCC583CCDFEADED8
:10041F00E880DB89828A83E493A3F208DFF980CC3A
:10042F0088F0EF60010E4E60C388F0ED2402B40433
:10043F000050B9F582EB2402B4040050AF232345DA
:06044F0082239003AF734D
:10000300E576246AF8E60576227867300702786A8F
:10001300E475F0011204AD0204552000EB7F2ED2EB
:10002300008018EF540F2490D43440D4FF30040BD5
:10003300EF24BFB41A0050032461FFE57760021573
:1000430077057AE57A7002057930070D7867E475EC
:10005300F0011204ADEF02049B02057B7403D20787
:100063008003E4C207F5768B678A688969E4F577CC
:10007300F579F57AE57760077F2012003E80F57504
:1000830078FFC201C200C202C203C205C206C2088F
:1000930012000CFF700D3007057F0012004FAF7A7E
:1000A300AE7922B4255FC2D5C20412000CFF24D05E
:1000B300B40A00501A75F00A787730D50508B6FFF0
:1000C3000106C6A426F620D5047002D20380D924E3
:1000D300CFB41A00EF5004C2E5D20402024FD2019A
:1000E30080C6D20080C0D20280BCD2D580BAD205ED
:1000F30080B47F2012003E2002077401B5770040D0
:10010300F1120003FF12003E020077D208D20680EC
:1001130095120003FB120003FA120003F94A4B7015
:100123000679207A037BFF20022EE577602A7E0082
:100133008E8275830012046E60060EEE657870F091
:10014300C2D5EBC0E0EAC0E0E9C0E0EE120296D00F
:10015300E0F9D0E0FAD0E0FB120455FF60AAEBC04F
:10016300E0EAC0E0E9C0E012003ED0E02401F9D0AB
:10017300E03400FAD0E0FBE5780460DCD578D98080
:10018300877BFF7A027992D202809C791080027970
:1001930008C206C2088008D2D5790A8004790AC247
:1001A300D5E578047002F578E4FAFDFEFF1200034A
:1001B300FC7B08200113120003FD7B1030000A12A0
:1001C3000003FE120003FF7B20EC3382D592D5504F
:1001D30013C3E43000069FFFE49EFEE42001039D69
:1001E300FDE49CFCE4CBF8C201EC700CCFCECDCC8B
:1001F300E824F8F870F38017C3EF33FFEE33FEED16
:1002030033FDEC33FCEB33FB994002FB0FD8E9EBF6
:10021300300105F8D0E0C448B201C0E00AEC4D4E0D
:100223004F78207B0070C2EAB5780040BCC0E01272
:100233000298D0F0D0E0200104C4C0E0C4B201C0F1
:10024300F0120027D0F0D5F0EB0200771204BD01C5
:100253001453018E5800E54C00E14201924F019A7C
:0F02630044019A4900FA4301A0550184460184E1
:100272004501844703405000E92D00ED2E01102B6B
:1002820000F123010E2003292A00A94800000108D9
:100292003F3F3F00790AA2D5200314300509B91067
:1002A200020404B9080104A2D52006025001042068
:1002B20002689202B577005034C0E07F2030031903
:1002C2007F30A20272067205500F1202EFC202C202
:1002D20006C205C2087F30800F300503E9C0E01274
:1002E200003E300503D0E0F9D0E0B577CC300517F9
:1002F2007F30B9100C12003E7F583004077F78809F
:1003020003B9080312003E3002057F2D02003E7F32
:10031200202008F87F2B2006F322920280CF286E3D
:10032200756C6C2900D2011200033001F8C2017809
:100332007730D50108F60200A92D50434958120022
:10034200032403B405004001E490033B9312002F01
:0D035200743A12002FD20375770402018E59
:10045500BB010689828A83E0225002E722BBFE02A5
:09046500E32289828A83E49322D8
:10046E00BB010CE58229F582E5833AF583E0225043
:10047E0006E92582F8E622BBFE06E92582F8E2228D
:0D048E00E58229F582E5833AF583E49322A7
:10049B00BB010689828A83F0225002F722BBFE0140
:0204AB00F3223A
:1004AD00FAE6FB0808E6F925F0F618E6CA3AF62250
:1004BD00D083D082F8E4937012740193700DA3A3CE
:1004CD0093F8740193F5828883E4737402936860E2
:0604DD00EFA3A3A380DFE2
:10057B00EFB40A07740D120586740A309811A89906
:10058B00B8130CC2983098FDA899C298B811F630E0
:07059B0099FDC299F59922B8
:00000001FF
'''
bin8 = array.array('B',[2, 5, 162, 229, 118, 36, 106, 248, 230, 5, 118, 34,
                        120, 103, 48, 7, 2, 120, 106, 228, 117, 240, 1, 18,
                        4, 173, 2, 4, 85, 32, 0, 235, 127, 46, 210, 0, 128,
                        24, 239, 84, 15, 36, 144, 212, 52, 64, 212, 255, 48,
                        4, 11, 239, 36, 191, 180, 26, 0, 80, 3, 36, 97, 255,
                        229, 119, 96, 2, 21, 119, 5, 122, 229, 122, 112, 2,
                        5, 121, 48, 7, 13, 120, 103, 228, 117, 240, 1, 18,
                        4, 173, 239, 2, 4, 155, 2, 5, 123, 116, 3, 210, 7,
                        128, 3, 228, 194, 7, 245, 118, 139, 103, 138, 104,
                        137, 105, 228, 245, 119, 245, 121, 245, 122, 229,
                        119, 96, 7, 127, 32, 18, 0, 62, 128, 245, 117, 120,
                        255, 194, 1, 194, 0, 194, 2, 194, 3, 194, 5, 194, 6,
                        194, 8, 18, 0, 12, 255, 112, 13, 48, 7, 5, 127, 0,
                        18, 0, 79, 175, 122, 174, 121, 34, 180, 37, 95, 194,
                        213, 194, 4, 18, 0, 12, 255, 36, 208, 180, 10, 0, 80,
                        26, 117, 240, 10, 120, 119, 48, 213, 5, 8, 182, 255,
                        1, 6, 198, 164, 38, 246, 32, 213, 4, 112, 2, 210, 3,
                        128, 217, 36, 207, 180, 26, 0, 239, 80, 4, 194, 229,
                        210, 4, 2, 2, 79, 210, 1, 128, 198, 210, 0, 128, 192,
                        210, 2, 128, 188, 210, 213, 128, 186, 210, 5, 128,
                        180, 127, 32, 18, 0, 62, 32, 2, 7, 116, 1, 181, 119,
                        0, 64, 241, 18, 0, 3, 255, 18, 0, 62, 2, 0, 119, 210,
                        8, 210, 6, 128, 149, 18, 0, 3, 251, 18, 0, 3, 250,
                        18, 0, 3, 249, 74, 75, 112, 6, 121, 32, 122, 3, 123,
                        255, 32, 2, 46, 229, 119, 96, 42, 126, 0, 142, 130,
                        117, 131, 0, 18, 4, 110, 96, 6, 14, 238, 101, 120,
                        112, 240, 194, 213, 235, 192, 224, 234, 192, 224,
                        233, 192, 224, 238, 18, 2, 150, 208, 224, 249, 208,
                        224, 250, 208, 224, 251, 18, 4, 85, 255, 96, 170,
                        235, 192, 224, 234, 192, 224, 233, 192, 224, 18, 0,
                        62, 208, 224, 36, 1, 249, 208, 224, 52, 0, 250, 208,
                        224, 251, 229, 120, 4, 96, 220, 213, 120, 217, 128,
                        135, 123, 255, 122, 2, 121, 146, 210, 2, 128, 156,
                        121, 16, 128, 2, 121, 8, 194, 6, 194, 8, 128, 8, 210,
                        213, 121, 10, 128, 4, 121, 10, 194, 213, 229, 120, 4,
                        112, 2, 245, 120, 228, 250, 253, 254, 255, 18, 0, 3,
                        252, 123, 8, 32, 1, 19, 18, 0, 3, 253, 123, 16, 48,
                        0, 10, 18, 0, 3, 254, 18, 0, 3, 255, 123, 32, 236,
                        51, 130, 213, 146, 213, 80, 19, 195, 228, 48, 0, 6,
                        159, 255, 228, 158, 254, 228, 32, 1, 3, 157, 253,
                        228, 156, 252, 228, 203, 248, 194, 1, 236, 112, 12,
                        207, 206, 205, 204, 232, 36, 248, 248, 112, 243, 128,
                        23, 195, 239, 51, 255, 238, 51, 254, 237, 51, 253,
                        236, 51, 252, 235, 51, 251, 153, 64, 2, 251, 15, 216,
                        233, 235, 48, 1, 5, 248, 208, 224, 196, 72, 178, 1,
                        192, 224, 10, 236, 77, 78, 79, 120, 32, 123, 0, 112,
                        194, 234, 181, 120, 0, 64, 188, 192, 224, 18, 2, 152,
                        208, 240, 208, 224, 32, 1, 4, 196, 192, 224, 196,
                        178, 1, 192, 240, 18, 0, 39, 208, 240, 213, 240, 235,
                        2, 0, 119, 18, 4, 189, 1, 20, 83, 1, 142, 88, 0, 229,
                        76, 0, 225, 66, 1, 146, 79, 1, 154, 68, 1, 154, 73,
                        0, 250, 67, 1, 160, 85, 1, 132, 70, 1, 132, 69, 1,
                        132, 71, 3, 64, 80, 0, 233, 45, 0, 237, 46, 1, 16,
                        43, 0, 241, 35, 1, 14, 32, 3, 41, 42, 0, 169, 72, 0,
                        0, 1, 8, 63, 63, 63, 0, 121, 10, 162, 213, 32, 3, 20,
                        48, 5, 9, 185, 16, 2, 4, 4, 185, 8, 1, 4, 162, 213,
                        32, 6, 2, 80, 1, 4, 32, 2, 104, 146, 2, 181, 119, 0,
                        80, 52, 192, 224, 127, 32, 48, 3, 25, 127, 48, 162,
                        2, 114, 6, 114, 5, 80, 15, 18, 2, 239, 194, 2, 194,
                        6, 194, 5, 194, 8, 127, 48, 128, 15, 48, 5, 3, 233,
                        192, 224, 18, 0, 62, 48, 5, 3, 208, 224, 249, 208,
                        224, 181, 119, 204, 48, 5, 23, 127, 48, 185, 16, 12,
                        18, 0, 62, 127, 88, 48, 4, 7, 127, 120, 128, 3, 185,
                        8, 3, 18, 0, 62, 48, 2, 5, 127, 45, 2, 0, 62, 127,
                        32, 32, 8, 248, 127, 43, 32, 6, 243, 34, 146, 2, 128,
                        207, 40, 110, 117, 108, 108, 41, 0, 210, 1, 18, 0, 3,
                        48, 1, 248, 194, 1, 120, 119, 48, 213, 1, 8, 246, 2,
                        0, 169, 45, 80, 67, 73, 88, 18, 0, 3, 36, 3, 180, 5,
                        0, 64, 1, 228, 144, 3, 59, 147, 18, 0, 47, 116, 58,
                        18, 0, 47, 210, 3, 117, 119, 4, 2, 1, 142, 231, 9,
                        246, 8, 223, 250, 128, 70, 231, 9, 242, 8, 223, 250,
                        128, 62, 136, 130, 140, 131, 231, 9, 240, 163, 223,
                        250, 128, 50, 227, 9, 246, 8, 223, 250, 128, 120,
                        227, 9, 242, 8, 223, 250, 128, 112, 136, 130, 140,
                        131, 227, 9, 240, 163, 223, 250, 128, 100, 137,
                        130, 138, 131, 224, 163, 246, 8, 223, 250, 128, 88,
                        137, 130, 138, 131, 224, 163, 242, 8, 223, 250, 128,
                        76, 128, 210, 128, 250, 128, 198, 128, 212, 128, 105,
                        128, 242, 128, 51, 128, 16, 128, 166, 128, 234, 128,
                        154, 128, 168, 128, 218, 128, 226, 128, 202, 128, 51,
                        137, 130, 138, 131, 236, 250, 228, 147, 163, 200,
                        197, 130, 200, 204, 197, 131, 204, 240, 163, 200,
                        197, 130, 200, 204, 197, 131, 204, 223, 233, 222,
                        231, 128, 13, 137, 130, 138, 131, 228, 147, 163, 246,
                        8, 223, 249, 236, 250, 169, 240, 237, 251, 34, 137,
                        130, 138, 131, 236, 250, 224, 163, 200, 197, 130,
                        200, 204, 197, 131, 204, 240, 163, 200, 197, 130,
                        200, 204, 197, 131, 204, 223, 234, 222, 232, 128,
                        219, 137, 130, 138, 131, 228, 147, 163, 242, 8,
                        223, 249, 128, 204, 136, 240, 239, 96, 1, 14, 78,
                        96, 195, 136, 240, 237, 36, 2, 180, 4, 0, 80, 185,
                        245, 130, 235, 36, 2, 180, 4, 0, 80, 175, 35, 35,
                        69, 130, 35, 144, 3, 175, 115, 187, 1, 6, 137, 130,
                        138, 131, 224, 34, 80, 2, 231, 34, 187, 254, 2, 227,
                        34, 137, 130, 138, 131, 228, 147, 34, 187, 1, 12,
                        229, 130, 41, 245, 130, 229, 131, 58, 245, 131, 224,
                        34, 80, 6, 233, 37, 130, 248, 230, 34, 187, 254, 6,
                        233, 37, 130, 248, 226, 34, 229, 130, 41, 245, 130,
                        229, 131, 58, 245, 131, 228, 147, 34, 187, 1, 6,
                        137, 130, 138, 131, 240, 34, 80, 2, 247, 34, 187,
                        254, 1, 243, 34, 250, 230, 251, 8, 8, 230, 249, 37,
                        240, 246, 24, 230, 202, 58, 246, 34, 208, 131, 208,
                        130, 248, 228, 147, 112, 18, 116, 1, 147, 112, 13,
                        163, 163, 147, 248, 116, 1, 147, 245, 130, 136,
                        131, 228, 115, 116, 2, 147, 104, 96, 239, 163, 163,
                        163, 128, 223, 207, 240, 251, 226, 253, 242, 32,
                        255, 32, 242, 225, 32, 226, 251, 230, 243, 10, 0,
                        253, 224, 225, 226, 227, 180, 228, 229, 186, 230,
                        231, 179, 191, 232, 233, 234, 235, 236, 237, 238,
                        239, 240, 241, 242, 243, 244, 245, 246, 247, 248,
                        249, 252, 254, 255, 0, 192, 193, 194, 195, 165, 196,
                        197, 170, 198, 199, 178, 175, 200, 201, 202, 203,
                        204, 205, 206, 207, 208, 209, 210, 211, 212, 213,
                        214, 215, 216, 217, 220, 222, 223, 0, 120, 34, 124,
                        0, 125, 0, 123, 255, 122, 4, 121, 245, 126, 0, 127,
                        35, 18, 4, 47, 120, 69, 124, 0, 125, 0, 123, 255,
                        122, 5, 121, 24, 126, 0, 127, 34, 18, 4, 47, 117,
                        152, 80, 67, 137, 32, 117, 141, 221, 210, 142, 210,
                        153, 99, 144, 1, 123, 255, 122, 4, 121, 227, 18, 0,
                        101, 128, 254, 239, 180, 10, 7, 116, 13, 18, 5, 134,
                        116, 10, 48, 152, 17, 168, 153, 184, 19, 12, 194,
                        152, 48, 152, 253, 168, 153, 194, 152, 184, 17,
                        246, 48, 153, 253, 194, 153, 245, 153, 34, 120, 127,
                        228, 246, 216, 253, 117, 129, 122, 2, 5, 58])


hex16 = """:020000040000FA
:10000000000083120313072055301820042883169C
:10001000031340309900181598168312031318160D
:1000200098170800831203138C1E14281A0808005E
:0C003000831203130C1E1A28990008000C
:00000001FF
"""
bin16 = array.array('H', [0x0000, 0x1283, 0x1303, 0x2007,
                          0x3055, 0x2018, 0x2804, 0x1683,
                          0x1303, 0x3040, 0x0099, 0x1518,
                          0x1698, 0x1283, 0x1303, 0x1618,
                          0x1798, 0x0008, 0x1283, 0x1303,
                          0x1E8C, 0x2814, 0x081A, 0x0008,
                          0x1283, 0x1303, 0x1E0C, 0x281A,
                          0x0099, 0x0008, 0x3FFF, 0x3FFF])


hex64k = """:020000040000FA
:0100000001FE
:020000040001F9
:0100000002FD
:00000001FF
"""
data64k = {0: 1, 0x10000: 2}


hex_rectype3 = """:0400000312345678E5
:0100000001FE
:00000001FF
"""
data_rectype3 = {0: 1}
start_addr_rectype3 = {'CS': 0x1234, 'IP': 0x5678}


hex_rectype5 = """:0400000512345678E3
:0100000002FD
:00000001FF
"""
data_rectype5 = {0: 2}
start_addr_rectype5 = {'EIP': 0x12345678}

hex_empty_file = ':00000001FF\n'

hex_simple = """\
:10000000000083120313072055301820042883169C
:10001000031340309900181598168312031318160D
:1000200098170800831203138C1E14281A0808005E
:0C003000831203130C1E1A28990008000C
:00000001FF
"""

hex_bug_lp_341051 = """\
:020FEC00E4E738
:040FF00022E122E1F7
:00000001FF
"""


##
# Test cases

class TestIntelHexBase(unittest.TestCase):
    """Base class for all tests.
    Provide additional functionality for testing.
    """

    def assertRaisesMsg(self, excClass, msg, callableObj, *args, **kwargs):
        """Just like unittest.TestCase.assertRaises,
        but checks that the message is right too.

        Borrowed from Ned Batchelder Blog.
        See: http://www.nedbatchelder.com/blog/200609.html#e20060905T064418

        Typical usage::

            self.assertRaisesMsg(MyException, "Exception message",
                                 my_function, (arg1, arg2))
        """
        try:
            callableObj(*args, **kwargs)
        except excClass:
            exc = sys.exc_info()[1]     # current exception
            excMsg = str(exc)
            if not msg:
                # No message provided: any message is fine.
                return
            elif excMsg == msg:
                # Message provided, and we got the right message: it passes.
                return
            else:
                # Message provided, and it didn't match: fail!
                raise self.failureException(
                    "Right exception, wrong message: got '%s' expected '%s'" %
                    (excMsg, msg)
                    )
        else:
            if hasattr(excClass, '__name__'):
                excName = excClass.__name__
            else:
                excName = str(excClass)
            raise self.failureException(
                "Expected to raise %s, didn't get an exception at all" %
                excName
                )

    def assertEqualWrittenData(self, a, b):
        return self.assertEqual(a, b, """Written data is incorrect
Should be:
%s

Written:
%s
""" % (a, b))
#/class TestIntelHexBase


class TestIntelHex(TestIntelHexBase):

    def setUp(self):
        self.f = StringIO(hex8)

    def tearDown(self):
        self.f.close()
        del self.f

    def test_init_from_file(self):
        ih = IntelHex(self.f)
        for addr in range_g(len(bin8)):
            expected = bin8[addr]
            actual = ih[addr]
            self.assertEqual(expected, actual,
                             "Data different at address "
                             "%x (%x != %x)" % (addr, expected, actual))

    def test_hex_fromfile(self):
        ih = IntelHex()
        ih.fromfile(self.f, format='hex')
        for addr in range_g(len(bin8)):
            expected = bin8[addr]
            actual = ih[addr]
            self.assertEqual(expected, actual,
                             "Data different at address "
                             "%x (%x != %x)" % (addr, expected, actual))

    def test_unicode_filename(self):
        handle, fname = tempfile.mkstemp(UnicodeType(''))
        os.close(handle)
        try:
            self.assertTrue(isinstance(fname, UnicodeType))
            f = open(fname, 'w')
            try:
                f.write(hex8)
            finally:
                f.close()
            ih = IntelHex(fname)
            self.assertEqual(0, ih.minaddr())
            self.assertEqual(len(bin8)-1, ih.maxaddr())
        finally:
            os.remove(fname)

    def test_tobinarray_empty(self):
        ih = IntelHex()
        ih.padding = 0xFF   # set-up explicit padding value and don't use pad parameter
        self.assertEqual(array.array('B', []), ih.tobinarray())
        self.assertEqual(array.array('B', []), ih.tobinarray(start=0))
        self.assertEqual(array.array('B', []), ih.tobinarray(end=2))
        self.assertEqual(array.array('B', [255,255,255]), ih.tobinarray(0,2))

    def test_tobinarray_with_size(self):
        ih = IntelHex(self.f)
        self.assertEqual(array.array('B', [2, 5, 162, 229, 118, 36, 106, 248]),
                         ih.tobinarray(size=8))   # from addr 0
        self.assertEqual(array.array('B', [120, 103, 48, 7, 2, 120, 106, 228]),
                         ih.tobinarray(start=12, size=8))
        self.assertEqual(array.array('B', [2, 5, 162, 229, 118, 36, 106, 248]),
                         ih.tobinarray(end=7, size=8))   # addr: 0..7, 8 bytes
        self.assertEqual(array.array('B', [120, 103, 48, 7, 2, 120, 106, 228]),
                         ih.tobinarray(end=19, size=8))  # addr: 12..19, 8 bytes
        self.assertRaises(ValueError, ih.tobinarray, start=0, end=7, size=8)
        self.assertRaises(ValueError, ih.tobinarray, end=3, size=8)
        self.assertRaises(ValueError, ih.tobinarray, size=0)
        self.assertRaises(ValueError, ih.tobinarray, size=-1)

    def test_tobinstr(self):
        ih = IntelHex(self.f)
        s1 = ih.tobinstr()
        s2 = array_tobytes(bin8)
        self.assertEqual(s2, s1, "data not equal\n%s\n\n%s" % (s1, s2))

    def test_tobinfile(self):
        ih = IntelHex(self.f)
        sio = BytesIO()
        ih.tobinfile(sio)
        s1 = sio.getvalue()
        sio.close()
        s2 = array_tobytes(bin8)
        self.assertEqual(s2, s1, "data not equal\n%s\n\n%s" % (s1, s2))
        # new API: .tofile universal method
        sio = BytesIO()
        ih.tofile(sio, format='bin')
        s1 = sio.getvalue()
        sio.close()
        s2 = array_tobytes(bin8)
        self.assertEqual(s2, s1, "data not equal\n%s\n\n%s" % (s1, s2))

    def test_tobinfile_realfile(self):
        ih = IntelHex(self.f)
        tf = tempfile.TemporaryFile(mode='wb')
        try:
            ih.tobinfile(tf)
        finally:
            tf.close()

    def test__get_eol_textfile(self):
        self.assertEqual('\n', IntelHex._get_eol_textfile('native', 'win32'))
        self.assertEqual('\n', IntelHex._get_eol_textfile('native', 'linux'))
        self.assertEqual('\n', IntelHex._get_eol_textfile('CRLF', 'win32'))
        self.assertEqual('\r\n', IntelHex._get_eol_textfile('CRLF', 'linux'))
        self.assertRaisesMsg(ValueError, "wrong eolstyle 'LF'",
            IntelHex._get_eol_textfile, 'LF', 'win32')

    def test_write_empty_hexfile(self):
        ih = intelhex.IntelHex()
        sio = StringIO()
        ih.write_hex_file(sio)
        s = sio.getvalue()
        sio.close()
        self.assertEqualWrittenData(hex_empty_file, s)

    def test_write_hexfile(self):
        ih = intelhex.IntelHex(StringIO(hex_simple))
        sio = StringIO()
        ih.write_hex_file(sio)
        s = sio.getvalue()
        sio.close()
        self.assertEqualWrittenData(hex_simple, s)
        # new API: .tofile universal method
        sio = StringIO()
        ih.tofile(sio, format='hex')
        s = sio.getvalue()
        sio.close()
        self.assertEqualWrittenData(hex_simple, s)

    def test_write_hex_bug_341051(self):
        ih = intelhex.IntelHex(StringIO(hex_bug_lp_341051))
        sio = StringIO()
        ih.tofile(sio, format='hex')
        s = sio.getvalue()
        sio.close()
        self.assertEqualWrittenData(hex_bug_lp_341051, s)

    def test_write_hex_first_extended_linear_address(self):
        ih = IntelHex({0x20000: 0x01})
        sio = StringIO()
        ih.write_hex_file(sio)
        s = sio.getvalue()
        sio.close()
        # should be
        r = [Record.extended_linear_address(2),
             Record.data(0x0000, [0x01]),
             Record.eof()]
        h = '\n'.join(r) + '\n'
        # compare
        self.assertEqual(h, s)

    def test_tofile_wrong_format(self):
        ih = IntelHex()
        sio = StringIO()
        self.assertRaises(ValueError, ih.tofile, sio, {'format': 'bad'})

    def test_todict(self):
        ih = IntelHex()
        self.assertEqual({}, ih.todict())
        ih = IntelHex(StringIO(hex64k))
        self.assertEqual(data64k, ih.todict())
        ih = IntelHex()
        ih[1] = 2
        ih.start_addr = {'EIP': 1234}
        self.assertEqual({1: 2, 'start_addr': {'EIP': 1234}}, ih.todict())

    def test_fromdict(self):
        ih = IntelHex()
        ih.fromdict({1:2, 3:4})
        self.assertEqual({1:2, 3:4}, ih.todict())
        ih.fromdict({1:5, 6:7})
        self.assertEqual({1:5, 3:4, 6:7}, ih.todict())
        ih = IntelHex()
        ih.fromdict({1: 2, 'start_addr': {'EIP': 1234}})
        self.assertEqual({1: 2, 'start_addr': {'EIP': 1234}}, ih.todict())
        # bad dict
        self.assertRaises(ValueError, ih.fromdict, {'EIP': 1234})
        self.assertRaises(ValueError, ih.fromdict, {-1: 1234})

    def test_init_from_obj(self):
        ih = IntelHex({1:2, 3:4})
        self.assertEqual({1:2, 3:4}, ih.todict())
        ih.start_addr = {'EIP': 1234}
        ih2 = IntelHex(ih)
        ih[1] = 5
        ih.start_addr = {'EIP': 5678}
        self.assertEqual({1:2, 3:4, 'start_addr': {'EIP': 1234}}, ih2.todict())
        self.assertNotEqual(id(ih), id(ih2))

    def test_dict_interface(self):
        ih = IntelHex()
        self.assertEqual(0xFF, ih[0])  # padding byte substitution
        ih[0] = 1
        self.assertEqual(1, ih[0])
        del ih[0]
        self.assertEqual({}, ih.todict())  # padding byte substitution

    def test_len(self):
        ih = IntelHex()
        self.assertEqual(0, len(ih))
        ih[2] = 1
        self.assertEqual(1, len(ih))
        ih[1000] = 2
        self.assertEqual(2, len(ih))

    def test__getitem__(self):
        ih = IntelHex()
        # simple cases
        self.assertEqual(0xFF, ih[0])
        ih[0] = 1
        self.assertEqual(1, ih[0])
        # big address
        self.assertEqual(0xFF, ih[2**32-1])
        # wrong addr type/value for indexing operations
        def getitem(index):
            return ih[index]
        self.assertRaisesMsg(TypeError,
            'Address should be >= 0.',
            getitem, -1)
        self.assertRaisesMsg(TypeError,
            "Address has unsupported type: %s" % type('foo'),
            getitem, 'foo')
        # new object with some data
        ih = IntelHex()
        ih[0] = 1
        ih[1] = 2
        ih[2] = 3
        ih[10] = 4
        # full copy via slicing
        ih2 = ih[:]
        self.assertTrue(isinstance(ih2, IntelHex))
        self.assertEqual({0:1, 1:2, 2:3, 10:4}, ih2.todict())
        # other slice operations
        self.assertEqual({}, ih[3:8].todict())
        self.assertEqual({0:1, 1:2}, ih[0:2].todict())
        self.assertEqual({0:1, 1:2}, ih[:2].todict())
        self.assertEqual({2:3, 10:4}, ih[2:].todict())
        self.assertEqual({0:1, 2:3, 10:4}, ih[::2].todict())
        self.assertEqual({10:4}, ih[3:11].todict())

    def test__setitem__(self):
        ih = IntelHex()
        # simple indexing operation
        ih[0] = 1
        self.assertEqual({0:1}, ih.todict())
        # errors
        def setitem(a,b):
            ih[a] = b
        self.assertRaisesMsg(TypeError,
            'Address should be >= 0.',
            setitem, -1, 0)
        self.assertRaisesMsg(TypeError,
            "Address has unsupported type: %s" % type('foo'),
            setitem, 'foo', 0)
        # slice operations
        ih[0:4] = range_l(4)
        self.assertEqual({0:0, 1:1, 2:2, 3:3}, ih.todict())
        ih[0:] = range_l(5,9)
        self.assertEqual({0:5, 1:6, 2:7, 3:8}, ih.todict())
        ih[:4] = range_l(9,13)
        self.assertEqual({0:9, 1:10, 2:11, 3:12}, ih.todict())
        # with step
        ih = IntelHex()
        ih[0:8:2] = range_l(4)
        self.assertEqual({0:0, 2:1, 4:2, 6:3}, ih.todict())
        # errors in slice operations
        # ih[1:2] = 'a'
        self.assertRaisesMsg(ValueError,
            'Slice operation expects sequence of bytes',
            setitem, slice(1,2,None), 'a')
        # ih[0:1] = [1,2,3]
        self.assertRaisesMsg(ValueError,
            'Length of bytes sequence does not match address range',
            setitem, slice(0,1,None), [1,2,3])
        # ih[:] = [1,2,3]
        self.assertRaisesMsg(TypeError,
            'Unsupported address range',
            setitem, slice(None,None,None), [1,2,3])
        # ih[:2] = [1,2,3]
        self.assertRaisesMsg(TypeError,
            'start address cannot be negative',
            setitem, slice(None,2,None), [1,2,3])
        # ih[0:-3:-1] = [1,2,3]
        self.assertRaisesMsg(TypeError,
            'stop address cannot be negative',
            setitem, slice(0,-3,-1), [1,2,3])

    def test__delitem__(self):
        ih = IntelHex()
        ih[0] = 1
        del ih[0]
        self.assertEqual({}, ih.todict())
        # errors
        def delitem(addr):
            del ih[addr]
        self.assertRaises(KeyError, delitem, 1)
        self.assertRaisesMsg(TypeError,
            'Address should be >= 0.',
            delitem, -1)
        self.assertRaisesMsg(TypeError,
            "Address has unsupported type: %s" % type('foo'),
            delitem, 'foo')
        # deleting slice
        del ih[0:1]     # no error here because of slicing
        #
        def ihex(size=8):
            ih = IntelHex()
            for i in range_g(size):
                ih[i] = i
            return ih
        ih = ihex(8)
        del ih[:]       # delete all data
        self.assertEqual({}, ih.todict())
        ih = ihex(8)
        del ih[2:6]
        self.assertEqual({0:0, 1:1, 6:6, 7:7}, ih.todict())
        ih = ihex(8)
        del ih[::2]
        self.assertEqual({1:1, 3:3, 5:5, 7:7}, ih.todict())

    def test_addresses(self):
        # empty object
        ih = IntelHex()
        self.assertEqual([], ih.addresses())
        self.assertEqual(None, ih.minaddr())
        self.assertEqual(None, ih.maxaddr())
        # normal object
        ih = IntelHex({1:2, 7:8, 10:0})
        self.assertEqual([1,7,10], ih.addresses())
        self.assertEqual(1, ih.minaddr())
        self.assertEqual(10, ih.maxaddr())

    def test__get_start_end(self):
        # test for private method _get_start_end
        # for empty object
        ih = IntelHex()
        self.assertRaises(intelhex.EmptyIntelHexError, ih._get_start_end)
        self.assertRaises(intelhex.EmptyIntelHexError, ih._get_start_end, size=10)
        self.assertEqual((0,9), ih._get_start_end(start=0, size=10))
        self.assertEqual((1,10), ih._get_start_end(end=10, size=10))
        # normal object
        ih = IntelHex({1:2, 7:8, 10:0})
        self.assertEqual((1,10), ih._get_start_end())
        self.assertEqual((1,10), ih._get_start_end(size=10))        
        self.assertEqual((0,9), ih._get_start_end(start=0, size=10))
        self.assertEqual((1,10), ih._get_start_end(end=10, size=10))

    def test_segments(self):
        # test that address segments are correctly summarized
        ih = IntelHex()
        sg = ih.segments()
        self.assertTrue(isinstance(sg, list))
        self.assertEqual(len(sg), 0)
        ih[0x100] = 0
        sg = ih.segments()
        self.assertTrue(isinstance(sg, list))
        self.assertEqual(len(sg), 1)
        self.assertTrue(isinstance(sg[0], tuple))
        self.assertTrue(len(sg[0]) == 2)
        self.assertTrue(sg[0][0] < sg[0][1])
        self.assertEqual(min(sg[0]), 0x100)
        self.assertEqual(max(sg[0]), 0x101)
        ih[0x101] = 1
        sg = ih.segments()
        self.assertTrue(isinstance(sg, list))
        self.assertEqual(len(sg), 1)
        self.assertTrue(isinstance(sg[0], tuple))
        self.assertTrue(len(sg[0]) == 2)
        self.assertTrue(sg[0][0] < sg[0][1])
        self.assertEqual(min(sg[0]), 0x100)
        self.assertEqual(max(sg[0]), 0x102)
        ih[0x200] = 2
        ih[0x201] = 3
        ih[0x202] = 4
        sg = ih.segments()
        self.assertTrue(isinstance(sg, list))
        self.assertEqual(len(sg), 2)
        self.assertTrue(isinstance(sg[0], tuple))
        self.assertTrue(len(sg[0]) == 2)
        self.assertTrue(sg[0][0] < sg[0][1])
        self.assertTrue(isinstance(sg[1], tuple))
        self.assertTrue(len(sg[1]) == 2)
        self.assertTrue(sg[1][0] < sg[1][1])
        self.assertEqual(min(sg[0]), 0x100)
        self.assertEqual(max(sg[0]), 0x102)
        self.assertEqual(min(sg[1]), 0x200)
        self.assertEqual(max(sg[1]), 0x203)
        ih[0x204] = 5
        sg = ih.segments()
        self.assertEqual(len(sg), 3)
        sg = ih.segments(min_gap=2)
        self.assertEqual(len(sg), 2)
        self.assertEqual(min(sg[1]), 0x200)
        self.assertEqual(max(sg[1]), 0x205)
        pass

class TestIntelHexLoadBin(TestIntelHexBase):

    def setUp(self):
        self.bytes = asbytes('0123456789')
        self.f = BytesIO(self.bytes)

    def tearDown(self):
        self.f.close()

    def test_loadbin(self):
        ih = IntelHex()
        ih.loadbin(self.f)
        self.assertEqual(0, ih.minaddr())
        self.assertEqual(9, ih.maxaddr())
        self.assertEqual(self.bytes, ih.tobinstr())

    def test_bin_fromfile(self):
        ih = IntelHex()
        ih.fromfile(self.f, format='bin')
        self.assertEqual(0, ih.minaddr())
        self.assertEqual(9, ih.maxaddr())
        self.assertEqual(self.bytes, ih.tobinstr())

    def test_loadbin_w_offset(self):
        ih = IntelHex()
        ih.loadbin(self.f, offset=100)
        self.assertEqual(100, ih.minaddr())
        self.assertEqual(109, ih.maxaddr())
        self.assertEqual(self.bytes, ih.tobinstr())

    def test_loadfile_format_bin(self):
        ih = IntelHex()
        ih.loadfile(self.f, format='bin')
        self.assertEqual(0, ih.minaddr())
        self.assertEqual(9, ih.maxaddr())
        self.assertEqual(self.bytes, ih.tobinstr())


class TestIntelHexStartingAddressRecords(TestIntelHexBase):

    def _test_read(self, hexstr, data, start_addr):
        sio = StringIO(hexstr)
        ih = IntelHex(sio)
        sio.close()
        # test data
        self.assertEqual(data, ih._buf,
                         "Internal buffer: %r != %r" %
                         (data, ih._buf))
        self.assertEqual(start_addr, ih.start_addr,
                         "Start address: %r != %r" %
                         (start_addr, ih.start_addr))

    def test_read_rectype3(self):
        self._test_read(hex_rectype3, data_rectype3, start_addr_rectype3)

    def test_read_rectype5(self):
        self._test_read(hex_rectype5, data_rectype5, start_addr_rectype5)

    def _test_write(self, hexstr, data, start_addr, write_start_addr=True):
        # prepare
        ih = IntelHex(None)
        ih._buf = data
        ih.start_addr = start_addr
        # write
        sio = StringIO()
        ih.write_hex_file(sio, write_start_addr)
        s = sio.getvalue()
        sio.close()
        # check
        self.assertEqualWrittenData(hexstr, s)

    def _test_dont_write(self, hexstr, data, start_addr):
        expected = ''.join(hexstr.splitlines(True)[1:])
        self._test_write(expected, data, start_addr, False)

    def test_write_rectype3(self):
        self._test_write(hex_rectype3, data_rectype3, start_addr_rectype3)

    def test_dont_write_rectype3(self):
        self._test_dont_write(hex_rectype3, data_rectype3, start_addr_rectype3)

    def test_write_rectype5(self):
        self._test_write(hex_rectype5, data_rectype5, start_addr_rectype5)

    def test_dont_write_rectype5(self):
        self._test_dont_write(hex_rectype5, data_rectype5, start_addr_rectype5)

    def test_write_invalid_start_addr_value(self):
        ih = IntelHex()
        ih.start_addr = {'foo': 1}
        sio = StringIO()
        self.assertRaises(InvalidStartAddressValueError, ih.write_hex_file, sio)


class TestIntelHex_big_files(TestIntelHexBase):
    """Test that data bigger than 64K read/write correctly"""

    def setUp(self):
        self.f = StringIO(hex64k)

    def tearDown(self):
        self.f.close()
        del self.f

    def test_readfile(self):
        ih = intelhex.IntelHex(self.f)
        for addr, byte in dict_items_g(data64k):
            readed = ih[addr]
            self.assertEqual(byte, readed,
                              "data not equal at addr %X "
                              "(%X != %X)" % (addr, byte, readed))

    def test_write_hex_file(self):
        ih = intelhex.IntelHex(self.f)
        sio = StringIO()
        ih.write_hex_file(sio)
        s = sio.getvalue()
        sio.close()
        self.assertEqualWrittenData(hex64k, s)


class TestIntelHexGetPutString(TestIntelHexBase):

    def setUp(self):
        self.ih = IntelHex()
        for i in range_g(10):
            self.ih[i] = i

    def test_gets(self):
        self.assertEqual(asbytes('\x00\x01\x02\x03\x04\x05\x06\x07'), self.ih.gets(0, 8))
        self.assertEqual(asbytes('\x07\x08\x09'), self.ih.gets(7, 3))
        self.assertRaisesMsg(intelhex.NotEnoughDataError,
            'Bad access at 0x1: '
            'not enough data to read 10 contiguous bytes',
            self.ih.gets, 1, 10)

    def test_puts(self):
        self.ih.puts(0x03, asbytes('hello'))
        self.assertEqual(asbytes('\x00\x01\x02hello\x08\x09'), self.ih.gets(0, 10))

    def test_getsz(self):
        self.assertEqual(asbytes(''), self.ih.getsz(0))
        self.assertRaisesMsg(intelhex.NotEnoughDataError,
            'Bad access at 0x1: '
            'not enough data to read zero-terminated string',
            self.ih.getsz, 1)
        self.ih[4] = 0
        self.assertEqual(asbytes('\x01\x02\x03'), self.ih.getsz(1))

    def test_putsz(self):
        self.ih.putsz(0x03, asbytes('hello'))
        self.assertEqual(asbytes('\x00\x01\x02hello\x00\x09'), self.ih.gets(0, 10))

    def test_find(self):
        self.assertEqual(0, self.ih.find(asbytes('\x00\x01\x02\x03\x04\x05\x06')))
        self.assertEqual(0, self.ih.find(asbytes('\x00')))
        self.assertEqual(3, self.ih.find(asbytes('\x03\x04\x05\x06')))
        self.assertEqual(3, self.ih.find(asbytes('\x03')))
        self.assertEqual(7, self.ih.find(asbytes('\x07\x08\x09')))
        self.assertEqual(7, self.ih.find(asbytes('\x07')))
        self.assertEqual(-1, self.ih.find(asbytes('\x0a')))
        self.assertEqual(-1, self.ih.find(asbytes('\x02\x01')))
        self.assertEqual(-1, self.ih.find(asbytes('\x08\x07')))

    def test_find_start(self):
        self.assertEqual(-1, self.ih.find(asbytes('\x00\x01\x02\x03\x04\x05\x06'), start=3))
        self.assertEqual(-1, self.ih.find(asbytes('\x00'), start=3))
        self.assertEqual(3, self.ih.find(asbytes('\x03\x04\x05\x06'), start=3))
        self.assertEqual(3, self.ih.find(asbytes('\x03'), start=3))
        self.assertEqual(7, self.ih.find(asbytes('\x07\x08\x09'), start=3))
        self.assertEqual(7, self.ih.find(asbytes('\x07'), start=3))
        self.assertEqual(-1, self.ih.find(asbytes('\x0a'), start=3))
        self.assertEqual(-1, self.ih.find(asbytes('\x02\x01'), start=3))
        self.assertEqual(-1, self.ih.find(asbytes('\x08\x07'), start=3))

    def test_find_end(self):
        self.assertEqual(-1, self.ih.find(asbytes('\x00\x01\x02\x03\x04\x05\x06'), end=4))
        self.assertEqual(0, self.ih.find(asbytes('\x00'), end=4))
        self.assertEqual(-1, self.ih.find(asbytes('\x03\x04\x05\x06'), end=4))
        self.assertEqual(3, self.ih.find(asbytes('\x03'), end=4))
        self.assertEqual(-1, self.ih.find(asbytes('\x07\x08\x09'), end=4))
        self.assertEqual(-1, self.ih.find(asbytes('\x07'), end=4))
        self.assertEqual(-1, self.ih.find(asbytes('\x0a'), end=4))
        self.assertEqual(-1, self.ih.find(asbytes('\x02\x01'), end=4))
        self.assertEqual(-1, self.ih.find(asbytes('\x08\x07'), end=4))

    def test_find_start_end(self):
        self.assertEqual(-1, self.ih.find(asbytes('\x00\x01\x02\x03\x04\x05\x06'), start=3, end=7))
        self.assertEqual(-1, self.ih.find(asbytes('\x00'), start=3, end=7))
        self.assertEqual(3, self.ih.find(asbytes('\x03\x04\x05\x06'), start=3, end=7))
        self.assertEqual(3, self.ih.find(asbytes('\x03'), start=3, end=7))
        self.assertEqual(-1, self.ih.find(asbytes('\x07\x08\x09'), start=3, end=7))
        self.assertEqual(-1, self.ih.find(asbytes('\x07'), start=3, end=7))
        self.assertEqual(-1, self.ih.find(asbytes('\x0a'), start=3, end=7))
        self.assertEqual(-1, self.ih.find(asbytes('\x02\x01'), start=3, end=7))
        self.assertEqual(-1, self.ih.find(asbytes('\x08\x07'), start=3, end=7))


class TestIntelHexDump(TestIntelHexBase):

    def test_empty(self):
        ih = IntelHex()
        sio = StringIO()
        ih.dump(sio)
        self.assertEqual('', sio.getvalue())

    def test_simple(self):
        ih = IntelHex()
        ih[0] = 0x12
        ih[1] = 0x34
        sio = StringIO()
        ih.dump(sio)
        self.assertEqual(
            '0000  12 34 -- -- -- -- -- -- -- -- -- -- -- -- -- --  |.4              |\n',
            sio.getvalue())
        ih[16] = 0x56
        ih[30] = 0x98
        sio = StringIO()
        ih.dump(sio)
        self.assertEqual(
            '0000  12 34 -- -- -- -- -- -- -- -- -- -- -- -- -- --  |.4              |\n'
            '0010  56 -- -- -- -- -- -- -- -- -- -- -- -- -- 98 --  |V             . |\n',
            sio.getvalue())

    def test_minaddr_not_zero(self):
        ih = IntelHex()
        ih[16] = 0x56
        ih[30] = 0x98
        sio = StringIO()
        ih.dump(sio)
        self.assertEqual(
            '0010  56 -- -- -- -- -- -- -- -- -- -- -- -- -- 98 --  |V             . |\n',
            sio.getvalue())

    def test_start_addr(self):
        ih = IntelHex()
        ih[0] = 0x12
        ih[1] = 0x34
        ih.start_addr = {'CS': 0x1234, 'IP': 0x5678}
        sio = StringIO()
        ih.dump(sio)
        self.assertEqual(
            'CS = 0x1234, IP = 0x5678\n'
            '0000  12 34 -- -- -- -- -- -- -- -- -- -- -- -- -- --  |.4              |\n',
            sio.getvalue())
        ih.start_addr = {'EIP': 0x12345678}
        sio = StringIO()
        ih.dump(sio)
        self.assertEqual(
            'EIP = 0x12345678\n'
            '0000  12 34 -- -- -- -- -- -- -- -- -- -- -- -- -- --  |.4              |\n',
            sio.getvalue())

    def test_bad_width(self):
        ih = IntelHex()
        sio = StringIO()
        badwidths = [0, -1, -10.5, 2.5]
        for bw in badwidths:
            self.assertRaisesMsg(ValueError, "width must be a positive integer.",
                ih.dump, sio, bw)
        badwidthtypes = ['', {}, [], sio]
        for bwt in badwidthtypes:
            self.assertRaisesMsg(ValueError, "width must be a positive integer.",
                ih.dump, sio, bwt)

    def test_simple_width3(self):
        ih = IntelHex()
        ih[0] = 0x12
        ih[1] = 0x34
        sio = StringIO()
        ih.dump(tofile=sio, width=3)
        self.assertEqual(
            '0000  12 34 --  |.4 |\n',
            sio.getvalue())
            
        ih[16] = 0x56
        ih[30] = 0x98
        sio = StringIO()
        ih.dump(tofile=sio, width=3)
        self.assertEqual(
            '0000  12 34 --  |.4 |\n'
            '0003  -- -- --  |   |\n'
            '0006  -- -- --  |   |\n'
            '0009  -- -- --  |   |\n'
            '000C  -- -- --  |   |\n'
            '000F  -- 56 --  | V |\n'
            '0012  -- -- --  |   |\n'
            '0015  -- -- --  |   |\n'
            '0018  -- -- --  |   |\n'
            '001B  -- -- --  |   |\n'
            '001E  98 -- --  |.  |\n',
            sio.getvalue())

    def test_minaddr_not_zero_width3_padding(self):
        ih = IntelHex()
        ih[17] = 0x56
        ih[30] = 0x98
        sio = StringIO()
        ih.dump(tofile=sio, width=3, withpadding=True)
        self.assertEqual(
            '000F  FF FF 56  |..V|\n'
            '0012  FF FF FF  |...|\n'
            '0015  FF FF FF  |...|\n'
            '0018  FF FF FF  |...|\n'
            '001B  FF FF FF  |...|\n'
            '001E  98 FF FF  |...|\n',
            sio.getvalue())


class TestIntelHexMerge(TestIntelHexBase):

    def test_merge_empty(self):
        ih1 = IntelHex()
        ih2 = IntelHex()
        ih1.merge(ih2)
        self.assertEqual({}, ih1.todict())

    def test_merge_simple(self):
        ih1 = IntelHex({0:1, 1:2, 2:3})
        ih2 = IntelHex({3:4, 4:5, 5:6})
        ih1.merge(ih2)
        self.assertEqual({0:1, 1:2, 2:3, 3:4, 4:5, 5:6}, ih1.todict())

    def test_merge_wrong_args(self):
        ih1 = IntelHex()
        self.assertRaisesMsg(TypeError, 'other should be IntelHex object',
            ih1.merge, {0:1})
        self.assertRaisesMsg(ValueError, "Can't merge itself",
            ih1.merge, ih1)
        ih2 = IntelHex()
        self.assertRaisesMsg(ValueError, "overlap argument should be either "
            "'error', 'ignore' or 'replace'",
            ih1.merge, ih2, overlap='spam')

    def test_merge_overlap(self):
        # error
        ih1 = IntelHex({0:1})
        ih2 = IntelHex({0:2})
        self.assertRaisesMsg(intelhex.AddressOverlapError,
            'Data overlapped at address 0x0',
            ih1.merge, ih2, overlap='error')
        # ignore
        ih1 = IntelHex({0:1})
        ih2 = IntelHex({0:2})
        ih1.merge(ih2, overlap='ignore')
        self.assertEqual({0:1}, ih1.todict())
        # replace
        ih1 = IntelHex({0:1})
        ih2 = IntelHex({0:2})
        ih1.merge(ih2, overlap='replace')
        self.assertEqual({0:2}, ih1.todict())

    def test_merge_start_addr(self):
        # this, None
        ih1 = IntelHex({'start_addr': {'EIP': 0x12345678}})
        ih2 = IntelHex()
        ih1.merge(ih2)
        self.assertEqual({'start_addr': {'EIP': 0x12345678}}, ih1.todict())
        # None, other
        ih1 = IntelHex()
        ih2 = IntelHex({'start_addr': {'EIP': 0x12345678}})
        ih1.merge(ih2)
        self.assertEqual({'start_addr': {'EIP': 0x12345678}}, ih1.todict())
        # this == other: no conflict
        ih1 = IntelHex({'start_addr': {'EIP': 0x12345678}})
        ih2 = IntelHex({'start_addr': {'EIP': 0x12345678}})
        ih1.merge(ih2)
        self.assertEqual({'start_addr': {'EIP': 0x12345678}}, ih1.todict())
        # this != other: conflict
        ## overlap=error
        ih1 = IntelHex({'start_addr': {'EIP': 0x12345678}})
        ih2 = IntelHex({'start_addr': {'EIP': 0x87654321}})
        self.assertRaisesMsg(AddressOverlapError,
            'Starting addresses are different',
            ih1.merge, ih2, overlap='error')
        ## overlap=ignore
        ih1 = IntelHex({'start_addr': {'EIP': 0x12345678}})
        ih2 = IntelHex({'start_addr': {'EIP': 0x87654321}})
        ih1.merge(ih2, overlap='ignore')
        self.assertEqual({'start_addr': {'EIP': 0x12345678}}, ih1.todict())
        ## overlap=replace
        ih1 = IntelHex({'start_addr': {'EIP': 0x12345678}})
        ih2 = IntelHex({'start_addr': {'EIP': 0x87654321}})
        ih1.merge(ih2, overlap='replace')
        self.assertEqual({'start_addr': {'EIP': 0x87654321}}, ih1.todict())


class TestIntelHex16bit(TestIntelHexBase):

    def setUp(self):
        self.f = StringIO(hex16)

    def tearDown(self):
        self.f.close()
        del self.f

    def test_init_from_file(self):
        ih = intelhex.IntelHex16bit(self.f)

    def test_init_from_ih(self):
        ih = intelhex.IntelHex(self.f)
        ih16 = intelhex.IntelHex16bit(ih)

    def test_default_padding(self):
        ih16 = intelhex.IntelHex16bit()
        self.assertEqual(0x0FFFF, ih16.padding)
        self.assertEqual(0x0FFFF, ih16[0])

    def test_minaddr(self):
        ih = intelhex.IntelHex16bit(self.f)
        addr = ih.minaddr()
        self.assertEqual(0, addr,
                         'Error in detection of minaddr (0 != 0x%x)' % addr)

    def test_maxaddr(self):
        ih = intelhex.IntelHex16bit(self.f)
        addr = ih.maxaddr()
        self.assertEqual(0x001D, addr,
                         'Error in detection of maxaddr '
                         '(0x001D != 0x%x)' % addr)

    def test_getitem(self):
        ih = intelhex.IntelHex16bit(self.f)
        ih.padding = 0x3FFF
        for addr, word in enumerate(bin16):
            self.assertEqual(word, ih[addr],
                             'Data mismatch at address '
                             '0x%x (0x%x != 0x%x)' % (addr, word, ih[addr]))

    def test_not_enough_data(self):
        ih = intelhex.IntelHex()
        ih[0] = 1
        ih16 = intelhex.IntelHex16bit(ih)
        self.assertRaisesMsg(BadAccess16bit,
                             'Bad access at 0x0: '
                             'not enough data to read 16 bit value',
                             lambda x: ih16[x],
                             0)

    def test_write_hex_file(self):
        ih = intelhex.IntelHex16bit(self.f)
        sio = StringIO()
        ih.write_hex_file(sio)
        s = sio.getvalue()
        sio.close()

        fin = StringIO(s)
        ih2 = intelhex.IntelHex16bit(fin)

        self.assertEqual(ih.tobinstr(), ih2.tobinstr(),
                         "Written hex file does not equal with original")

    def test_bug_988148(self):
        # see https://bugs.launchpad.net/intelhex/+bug/988148
        ih = intelhex.IntelHex16bit(intelhex.IntelHex())
        ih[0] = 25
        sio = StringIO()
        ih.write_hex_file(sio)

    def test_setitem(self):
        ih = intelhex.IntelHex16bit(self.f)

        old = ih[0]
        ih[0] = old ^ 0xFFFF

        self.assertNotEqual(old, ih[0],
                            "Setting new value to internal buffer failed")

    def test_tobinarray(self):
        ih = intelhex.IntelHex16bit()
        ih[0] = 0x1234
        ih[1] = 0x5678
        self.assertEqual(array.array('H', [0x1234,0x5678,0xFFFF]),
                         ih.tobinarray(start=0, end=2))
        # change padding
        ih.padding = 0x3FFF
        self.assertEqual(array.array('H', [0x1234,0x5678,0x3FFF]),
                         ih.tobinarray(start=0, end=2))
#/class TestIntelHex16bit


class TestIntelHexErrors(TestIntelHexBase):
    """Tests for custom errors classes"""

    def assertEqualExc(self, message, exception):
        return self.assertEqual(message, str(exception))

    def test_IntelHexError(self):
        self.assertEqualExc('IntelHex base error', IntelHexError())

    def test_IntelHexError_message(self):
        self.assertEqualExc('IntelHex custom error message',
            IntelHexError(msg='IntelHex custom error message'))
        self.assertEqualExc('IntelHex base error', IntelHexError(msg=''))

    def test_HexReaderError(self):
        self.assertEqualExc('Hex reader base error', HexReaderError())

    def test_HexRecordError(self):
        self.assertEqualExc('Hex file contains invalid record at line 1',
            HexRecordError(line=1))

    def test_RecordLengthError(self):
        self.assertEqualExc('Record at line 1 has invalid length',
            RecordLengthError(line=1))

    def test_RecordTypeError(self):
        self.assertEqualExc('Record at line 1 has invalid record type',
            RecordTypeError(line=1))

    def test_RecordChecksumError(self):
        self.assertEqualExc('Record at line 1 has invalid checksum',
            RecordChecksumError(line=1))

    def test_EOFRecordError(self):
        self.assertEqualExc('File has invalid End-of-File record',
            EOFRecordError())

    def test_ExtendedSegmentAddressRecordError(self):
        self.assertEqualExc(
            'Invalid Extended Segment Address Record at line 1',
            ExtendedSegmentAddressRecordError(line=1))

    def test_ExtendedLinearAddressRecordError(self):
        self.assertEqualExc('Invalid Extended Linear Address Record at line 1',
            ExtendedLinearAddressRecordError(line=1))

    def test_StartSegmentAddressRecordError(self):
        self.assertEqualExc('Invalid Start Segment Address Record at line 1',
            StartSegmentAddressRecordError(line=1))

    def test_StartLinearAddressRecordError(self):
        self.assertEqualExc('Invalid Start Linear Address Record at line 1',
            StartLinearAddressRecordError(line=1))

    def test_DuplicateStartAddressRecord(self):
        self.assertEqualExc('Start Address Record appears twice at line 1',
            DuplicateStartAddressRecordError(line=1))

    def test_InvalidStartAddressValue(self):
        self.assertEqualExc("Invalid start address value: {'foo': 1}",
            InvalidStartAddressValueError(start_addr={'foo': 1}))

    def test_AddressOverlapError(self):
        self.assertEqualExc('Hex file has data overlap at address 0x1234 '
                            'on line 1',
                            AddressOverlapError(address=0x1234, line=1))

    def test_NotEnoughDataError(self):
        self.assertEqualExc('Bad access at 0x1234: '
            'not enough data to read 10 contiguous bytes',
            intelhex.NotEnoughDataError(address=0x1234, length=10))

    def test_BadAccess16bit(self):
        self.assertEqualExc('Bad access at 0x1234: '
                            'not enough data to read 16 bit value',
                            BadAccess16bit(address=0x1234))
#/class TestIntelHexErrors


class TestDecodeHexRecords(TestIntelHexBase):
    """Testing that decoding of records is correct
    and all errors raised when needed
    """

    def setUp(self):
        self.ih = IntelHex()
        self.decode_record = self.ih._decode_record

    def tearDown(self):
        del self.ih

    def test_empty_line(self):
        # do we could to accept empty lines in hex files?
        # standard don't say anything about this
        self.decode_record('')

    def test_non_empty_line(self):
        self.assertRaisesMsg(HexRecordError,
                             'Hex file contains invalid record at line 1',
                             self.decode_record,
                             ' ',
                             1)

    def test_short_record(self):
        # if record too short it's not a hex record
        self.assertRaisesMsg(HexRecordError,
                             'Hex file contains invalid record at line 1',
                             self.decode_record,
                             ':',
                             1)

    def test_odd_hexascii_digits(self):
        self.assertRaisesMsg(HexRecordError,
                             'Hex file contains invalid record at line 1',
                             self.decode_record,
                             ':0100000100F',
                             1)

    def test_invalid_length(self):
        self.assertRaisesMsg(RecordLengthError,
                             'Record at line 1 has invalid length',
                             self.decode_record,
                             ':FF00000100',
                             1)

    def test_invalid_record_type(self):
        self.assertRaisesMsg(RecordTypeError,
                             'Record at line 1 has invalid record type',
                             self.decode_record,
                             ':000000FF01',
                             1)

    def test_invalid_checksum(self):
        self.assertRaisesMsg(RecordChecksumError,
                             'Record at line 1 has invalid checksum',
                             self.decode_record,
                             ':0000000100',
                             1)

    def test_invalid_eof(self):
        self.assertRaisesMsg(EOFRecordError,
                             'File has invalid End-of-File record',
                             self.decode_record,
                             ':0100000100FE',
                             1)

    def test_invalid_extended_segment(self):
        # length
        self.assertRaisesMsg(ExtendedSegmentAddressRecordError,
                             'Invalid Extended Segment Address Record at line 1',
                             self.decode_record,
                             ':00000002FE',
                             1)
        # addr field
        self.assertRaisesMsg(ExtendedSegmentAddressRecordError,
                             'Invalid Extended Segment Address Record at line 1',
                             self.decode_record,
                             ':020001020000FB',
                             1)

    def test_invalid_linear_address(self):
        # length
        self.assertRaisesMsg(ExtendedLinearAddressRecordError,
                             'Invalid Extended Linear Address Record '
                             'at line 1',
                             self.decode_record,
                             ':00000004FC',
                             1)
        # addr field
        self.assertRaisesMsg(ExtendedLinearAddressRecordError,
                             'Invalid Extended Linear Address Record '
                             'at line 1',
                             self.decode_record,
                             ':020001040000F9',
                             1)

    def test_invalid_start_segment_addr(self):
        # length
        self.assertRaisesMsg(StartSegmentAddressRecordError,
                             'Invalid Start Segment Address Record at line 1',
                             self.decode_record,
                             ':00000003FD',
                             1)
        # addr field
        self.assertRaisesMsg(StartSegmentAddressRecordError,
                             'Invalid Start Segment Address Record at line 1',
                             self.decode_record,
                             ':0400010300000000F8',
                             1)

    def test_duplicate_start_segment_addr(self):
        self.decode_record(':0400000312345678E5')
        self.assertRaisesMsg(DuplicateStartAddressRecordError,
                             'Start Address Record appears twice at line 2',
                             self.decode_record,
                             ':0400000300000000F9',
                             2)

    def test_invalid_start_linear_addr(self):
        # length
        self.assertRaisesMsg(StartLinearAddressRecordError,
                             'Invalid Start Linear Address Record at line 1',
                             self.decode_record,
                             ':00000005FB',
                             1)
        # addr field
        self.assertRaisesMsg(StartLinearAddressRecordError,
                             'Invalid Start Linear Address Record at line 1',
                             self.decode_record,
                             ':0400010500000000F6',
                             1)

    def test_duplicate_start_linear_addr(self):
        self.decode_record(':0400000512345678E3')
        self.assertRaisesMsg(DuplicateStartAddressRecordError,
                             'Start Address Record appears twice at line 2',
                             self.decode_record,
                             ':0400000500000000F7',
                             2)

    def test_addr_overlap(self):
        self.decode_record(':0100000000FF')
        self.assertRaisesMsg(AddressOverlapError,
                             'Hex file has data overlap at address 0x0 '
                             'on line 1',
                             self.decode_record,
                             ':0100000000FF',
                             1)

    def test_data_record(self):
        # should be no exceptions
        self.decode_record(':0100000000FF\n')
        self.decode_record(':03000100000102F9\r\n')
        self.decode_record(':1004E300CFF0FBE2FDF220FF20F2E120E2FBE6F396')

    def test_eof(self):
        # EOF should raise special exception
        self.assertRaises(_EndOfFile, self.decode_record, ':00000001FF')

#/class TestDecodeHexRecords


class TestHex2Bin(unittest.TestCase):

    def setUp(self):
        self.fin = StringIO(hex8)
        self.fout = BytesIO()

    def tearDown(self):
        self.fin.close()
        self.fout.close()

    def test_hex2bin(self):
        ih = hex2bin(self.fin, self.fout)
        data = array.array('B', asbytes(self.fout.getvalue()))
        for addr in range_g(len(bin8)):
            expected = bin8[addr]
            actual = data[addr]
            self.assertEqual(expected, actual,
                             "Data different at address "
                             "%x (%x != %x)" % (addr, expected, actual))


class TestDiffDumps(unittest.TestCase):

    def test_simple(self):
        ih1 = IntelHex({1:0x30, 20:0x31, 40:0x33})
        ih2 = IntelHex({1:0x30, 20:0x32, 40:0x33})
        sio = StringIO()
        intelhex.diff_dumps(ih1, ih2, sio)
        result = sio.getvalue()
        extra = ' '
        if sys.version_info[0] >= 3 or sys.version >= '2.7':
            extra = ''
        shouldbe = (
            "--- a%(extra)s\n"
            "+++ b%(extra)s\n"
            "@@ -1,3 +1,3 @@\n"
            " 0000  -- 30 -- -- -- -- -- -- -- -- -- -- -- -- -- --  | 0              |\n"
            "-0010  -- -- -- -- 31 -- -- -- -- -- -- -- -- -- -- --  |    1           |\n"
            "+0010  -- -- -- -- 32 -- -- -- -- -- -- -- -- -- -- --  |    2           |\n"
            " 0020  -- -- -- -- -- -- -- -- 33 -- -- -- -- -- -- --  |        3       |\n"
            ) % dict(extra=extra)
        self.assertEqual(shouldbe, result)


class TestBuildRecords(TestIntelHexBase):

    def test__from_bytes(self):
        self.assertEqual(':00000001FF',
            intelhex.Record._from_bytes([0,0,0,1]))

    def test_data(self):
        self.assertEqual(':011234005663', intelhex.Record.data(0x1234, [0x56]))
        self.assertEqual(':0312340056789059',
            intelhex.Record.data(0x1234, [0x56, 0x78, 0x90]))

    def test_eof(self):
        self.assertEqual(':00000001FF', intelhex.Record.eof())

    def test_extended_segment_address(self):
        self.assertEqual(':020000021234B6',
            intelhex.Record.extended_segment_address(0x1234))

    def test_start_segment_address(self):
        self.assertEqual(':0400000312345678E5',
            intelhex.Record.start_segment_address(0x1234, 0x5678))

    def test_extended_linear_address(self):
        self.assertEqual(':020000041234B4',
            intelhex.Record.extended_linear_address(0x1234))

    def test_start_linear_address(self):
        self.assertEqual(':0400000512345678E3',
            intelhex.Record.start_linear_address(0x12345678))


class Test_GetFileAndAddrRange(TestIntelHexBase):

    def test_simple(self):
        self.assertEqual(('filename.hex', None, None),
            intelhex._get_file_and_addr_range('filename.hex'))
        self.assertEqual(('f', None, None),
            intelhex._get_file_and_addr_range('f'))
        self.assertEqual(('filename.hex', 1, None),
            intelhex._get_file_and_addr_range('filename.hex:1:'))
        self.assertEqual(('filename.hex', None, 10),
            intelhex._get_file_and_addr_range('filename.hex::A'))
        self.assertEqual(('filename.hex', 1, 10),
            intelhex._get_file_and_addr_range('filename.hex:1:A'))
        self.assertEqual(('filename.hex', 1, 10),
            intelhex._get_file_and_addr_range('filename.hex:0001:000A'))

    def test_bad_notation(self):
        self.assertRaises(intelhex._BadFileNotation,
            intelhex._get_file_and_addr_range, 'filename.hex:')
        self.assertRaises(intelhex._BadFileNotation,
            intelhex._get_file_and_addr_range, 'filename.hex:::')
        self.assertRaises(intelhex._BadFileNotation,
            intelhex._get_file_and_addr_range, 'C:\\filename.hex:', True)

    def test_drive_letter(self):
        self.assertEqual(('C:\\filename.hex', None, None),
            intelhex._get_file_and_addr_range('C:\\filename.hex', True))
        self.assertEqual(('C:\\filename.hex', 1, None),
            intelhex._get_file_and_addr_range('C:\\filename.hex:1:', True))
        self.assertEqual(('C:\\filename.hex', None, 10),
            intelhex._get_file_and_addr_range('C:\\filename.hex::A', True))
        self.assertEqual(('C:\\filename.hex', 1, 10),
            intelhex._get_file_and_addr_range('C:\\filename.hex:1:A', True))
        self.assertEqual(('C:\\filename.hex', 1, 10),
            intelhex._get_file_and_addr_range('C:\\filename.hex:0001:000A', True))


class TestXrangeLongInt(unittest.TestCase):

    def test_xrange_longint(self):
        # Bug #1408934: xrange(longint) blows with OverflowError:
        if compat.Python == 2:
            self.assertRaises(OverflowError, xrange, sys.maxint, sys.maxint+3)
        #
        upr = compat.range_g(2684625744, 2684625747)
        self.assertEqual([2684625744, 2684625745, 2684625746], list(upr))
        upr = compat.range_g(2684625744, 2684625747, 2)
        self.assertEqual([2684625744, 2684625746], list(upr))
        #
        dnr = compat.range_g(2684625746, 2684625743, -1)
        self.assertEqual([2684625746, 2684625745, 2684625744], list(dnr))
        dnr = compat.range_g(2684625746, 2684625743, -2)
        self.assertEqual([2684625746, 2684625744], list(dnr))


class TestInSubprocess(unittest.TestCase):

    def runProcessAndGetAsciiStdoutOrStderr(self, cmdline):
        if sys.platform != 'win32':
            cmdline = shlex.split(cmdline)
        p = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        retcode = p.poll()
        if stdout:
            output = stdout.decode('ascii', 'replace')
        elif stderr:
            output = stderr.decode('ascii', 'replace')        
        output = output.replace('\r', '')
        return retcode, output

    def versionChecker(self, cmdline_template):
        cmdline = cmdline_template % sys.executable
        retcode, output = self.runProcessAndGetAsciiStdoutOrStderr(cmdline)
        self.assertEqual(version_str, output.rstrip())
        self.assertEqual(0, retcode)

    def test_setup_version(self):
        self.versionChecker('%s setup.py --version')

    def test_sripts_bin2hex_version(self):
        self.versionChecker('%s scripts/bin2hex.py --version')

    def test_sripts_hex2bin_version(self):
        self.versionChecker('%s scripts/hex2bin.py --version')

    def test_sripts_hex2dump_version(self):
        self.versionChecker('%s scripts/hex2dump.py --version')

    def test_sripts_hexdiff_version(self):
        self.versionChecker('%s scripts/hexdiff.py --version')

    def test_sripts_hexmerge_version(self):
        self.versionChecker('%s scripts/hexmerge.py --version')


class TestWriteHexFileByteCount(unittest.TestCase):

    def setUp(self):
        self.f = StringIO(hex8)

    def tearDown(self):
        self.f.close()
        del self.f

    def test_write_hex_file_bad_byte_count(self):
        ih = intelhex.IntelHex(self.f)
        sio = StringIO()
        self.assertRaises(ValueError, ih.write_hex_file, sio, byte_count=0)
        self.assertRaises(ValueError, ih.write_hex_file, sio, byte_count=-1)
        self.assertRaises(ValueError, ih.write_hex_file, sio, byte_count=256)

    def test_write_hex_file_byte_count_1(self):
        ih = intelhex.IntelHex(self.f)
        ih1 = ih[:4]
        sio = StringIO()
        ih1.write_hex_file(sio, byte_count=1)
        s = sio.getvalue()
        sio.close()
        # check that we have all data records with data length == 1
        self.assertEqual((
            ':0100000002FD\n'
            ':0100010005F9\n'
            ':01000200A25B\n'
            ':01000300E517\n'
            ':00000001FF\n'
            ), s,
            "Written hex is not in byte count 1")
        # read back and check content
        fin = StringIO(s)
        ih2 = intelhex.IntelHex(fin)
        self.assertEqual(ih1.tobinstr(), ih2.tobinstr(),
                         "Written hex file does not equal with original")

    def test_write_hex_file_byte_count_13(self):
        ih = intelhex.IntelHex(self.f)
        sio = StringIO()
        ih.write_hex_file(sio, byte_count=13)
        s = sio.getvalue()
        # control written hex first line to check that byte count is 13
        sio.seek(0)
        self.assertEqual(sio.readline(), 
            ':0D0000000205A2E576246AF8E6057622786E\n',
            "Written hex is not in byte count 13")
        sio.close()

        fin = StringIO(s)
        ih2 = intelhex.IntelHex(fin)

        self.assertEqual(ih.tobinstr(), ih2.tobinstr(),
                         "Written hex file does not equal with original")

    def test_write_hex_file_byte_count_255(self):
        ih = intelhex.IntelHex(self.f)
        sio = StringIO()
        ih.write_hex_file(sio, byte_count=255)
        s = sio.getvalue()
        # control written hex first line to check that byte count is 255
        sio.seek(0)
        self.assertEqual(sio.readline(), 
            (':FF0000000205A2E576246AF8E60576227867300702786AE475F0011204AD02'
              '04552000EB7F2ED2008018EF540F2490D43440D4FF30040BEF24BFB41A0050'
              '032461FFE57760021577057AE57A7002057930070D7867E475F0011204ADEF'
              '02049B02057B7403D2078003E4C207F5768B678A688969E4F577F579F57AE5'
              '7760077F2012003E80F57578FFC201C200C202C203C205C206C20812000CFF'
              '700D3007057F0012004FAF7AAE7922B4255FC2D5C20412000CFF24D0B40A00'
              '501A75F00A787730D50508B6FF0106C6A426F620D5047002D20380D924CFB4'
              '1A00EF5004C2E5D20402024FD20180C6D20080C0D20280BCD2D580BAD20580'
              'B47F2012003E20020774010E\n'),
            "Written hex is not in byte count 255")
        sio.close()

        fin = StringIO(s)
        ih2 = intelhex.IntelHex(fin)

        self.assertEqual(ih.tobinstr(), ih2.tobinstr(),
                         "Written hex file does not equal with original")

##
# MAIN
if __name__ == '__main__':
    unittest.main()
