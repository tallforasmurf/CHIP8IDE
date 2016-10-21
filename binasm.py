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
