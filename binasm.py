__license__ = '''
 License (GPL-3.0) :
    This file is part of CHIP8IDE.

    CHIP8IDE is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You can find a copy of the GNU General Public License in the file
    COPYING.TXT included in the distribution of this program, or see:
    <http://www.gnu.org/licenses/>.
'''
__version__ = "1.0.0"
__author__  = "David Cortesi"
__copyright__ = "Copyright 2016 David Cortesi"
__maintainer__ = "David Cortesi"
__email__ = "davecortesi@gmail.com"

# This is a hack to make unit tests easier to code.
#
# Input to binasm is a string consisting of hex characters and spaces.
# Spaces are ignored. Each pair of hex characters is converted to a byte
# value. The string of bytes is returned as a list of ints.
#
from typing import List

def binasm( code : str ) -> List[int] :
    # Make it uppercase and discard non-hex chars
    hex = '0123456789ABCDEF'
    chars = [ c for c in code.upper() if c in hex ]
    assert len(chars)
    assert 0 == len(chars) % 2
    # there's probably a cleverer way to do this, but
    out = []
    i = 0
    while i < len( chars ) :
        n = ( 16 * hex.index( chars[i] ) ) + hex.index( chars[i+1] )
        out.append( int(n) )
        i += 2
    return out

# Following are hex strings from the early articles and manuals
#
# display an 8 in a moving pattern
#
P1 = 'A210 6100 6200 D125 D125 7101 7201 1206 F090 F090 F000'
#
# Continually increment V3 and display it as decimal
#
P2 = '''
6300 A300 F333 F265 6400 6500 4029 D455 7405
F129 D455 7405 F229 D455 6603 F618 6620
F615 F607 3600 1224 7301 00E0 1202
'''
#
# supposedly a 15s puzzle
#
P3 = '''
 00 e0 6c 00 4c 00 6e 0f a2 03 60 20 f0 55 00 e0
 22 be 22 76 22 8e 22 5e 22 46 12 10 61 00 62 17
 63 04 41 10 00 ee a2 e8 f1 1e f0 65 40 00 12 34
 f0 29 d2 35 71 01 72 05 64 03 84 12 34 00 12 22
 62 17 73 06 12 22 64 03 84 e2 65 03 85 d2 94 50
 00 ee 44 03 00 ee 64 01 84 e4 22 a6 12 46 64 03
 84 e2 65 03 85 d2 94 50 00 ee 44 00 00 ee 64 ff
 84 e4 22 a6 12 5e 64 0c 84 e2 65 0c 85 d2 94 50
 00 ee 44 00 00 ee 64 fc 84 e4 22 a6 12 76 64 0c
 84 e2 65 0c 85 d2 94 50 00 ee 44 0c 00 ee 64 04
 84 e4 22 a6 12 8e a2 e8 f4 1e f0 65 a2 e8 fe 1e
 f0 55 60 00 a2 e8 f4 1e f0 55 8e 40 00 ee 3c 00
 12 d2 22 1c 22 d8 22 1c a2 f8 fd 1e f0 65 8d 00
 00 ee 7c ff cd 0f 00 ee 7d 01 60 0f 8d 02 ed 9e
 12 d8 ed a1 12 e2 00 ee 01 02 03 04 05 06 07 08
 09 0a 0b 0c 0d 0e 0f 00 0d 00 01 02 04 05 06 08
 09 0a 0c 0e 03 07 0b 0f 84 e4 22 a6 12 76 64 0c
 84 e2 65 0c 85 d2 94 50 00 ee 44 0c 00 ee 64 04
 84 e4 22 a6 12 8e a2 e8 f4 1e f0 65 a2 e8 fe 1e
 f0 55 60 00 a2 e8 f4 1e f0 55 8e 40 00 ee 3c 00
 12 d2 22 1c 22 d8 22 1c a2 f8 fd 1e f0 65 8d 00
 00 ee 7c ff cd 0f 00 ee 7d 01 60 0f 8d 02 ed 9e
 12 d8 ed a1 12 e2 00 ee 01 02 03 04 05 06 07 08
 09 0a 0b 0c 0d 0e 0f 00 0d 00 01 02 04 05 06 08
'''
