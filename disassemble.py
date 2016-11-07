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

'''

    CHIP-8 IDE DISASSEMBLER

This is a sub-module of the source.py module, which implements the source
editor window.

The code here implements the dis-assembly of what is presumed to be a binary
executable for the CHIP-8 or SCHIP emulator. The File>Open code reads the
whole of the selected file as raw bytes. When that will not decode to a
Latin-1 text, it just passes those bytes here.

This will disassemble anything whether it is a CHIP-8 program or not. Any two
bytes that are a valid S/CHIP instruction are converted to assembler source.

Any byte that is not the opening byte of a valid instruction, is assembled as
a DB directive.

Addresses that are targets of jump, call or LD I instructions are defined
as labels on the statements they address, if possible; otherwise they are
defined as EQU statements.

'''

__all__ = [ 'disassemble' ]

'''
Store addresses which are targets of jump, call, or LD I instructions.
Generate matching labels of the form LBL0XXX at the appropriate places.
'''
TARGET_SET = set()

def add_label( b1:int, b2:int ) -> int :
    global TARGET_SET
    '''
    Given the two bytes of a 1xxx, 2xxx, Axxx or Bxxx instruction,
    extract the address value and return it, also adding it to
    the TARGET_SET
    '''
    address = ( ( b1 & 0x0F ) << 8) | b2
    TARGET_SET.add( address )
    return address

'''
The following functions perform the decode of individual instructions, based
on indexing a lambda by some part of the instruction.

Every lambda and function following takes two bytes of a presumed
instruction, b1 and b2, and returns a string representing an assembler
statement.

If the bytes do not decode to a known instruction, they return a null string.
'''


decode_00xx = {
    0x00E0 : 'CLS',          # 00E0 clear the display
    0x00EE : 'RET',          # 00EE return from subroutine
    0x00FB : 'SCR',          # 00FB scroll right 4 pixels (2 pixels in CHIP8 mode)
    0x00FC : 'SCL',          # 00FC scroll left 4 pixels (2 pixels in CHIP8 mode)
    0x00FD : 'EXIT',         # 00FD exit the emulator
    0x00FE : 'LOW',          # 00FE set CHIP-8 graphics (32x64)
    0x00FF : 'HIGH'          # 00FF set SCHIP graphics (64x128)
    }

def disasm_00xx( b1:int, b2:int ) -> str :
    '''
    b1 first nybble is 0, but for these instructions to be valid
    (and not random data that starts 0x) we need the 2nd nybble
    also to be 0.
    '''
    if b1 == 0 :
        if b2 in decode_00xx :
            return decode_00xx[ b2 ]
        if b2 in range( 0xC0, 0xD0 ) :
            return 'SCD #{:02X}'.format( b2 & 0x0f )
    return ''

decode_8xxx = {
    0x00 : lambda b1, b2: 'LD V{:1X}, V{:1X}'.format(
                              (b1 & 0x0f), (b2 >> 4) ),        # 8ts0 LD vt, vs
    0x01 : lambda b1, b2: 'OR V{:1X}, V{:1X}'.format(
                              (b1 & 0x0f), (b2 >> 4) ),        # 8ts1 OR vt, vs
    0x02 : lambda b1, b2: 'AND V{:1X}, V{:1X}'.format(
                              (b1 & 0x0f), (b2 >> 4) ),        # 8ts2 AND vt, vs
    0x03 : lambda b1, b2: 'XOR V{:1X}, V{:1X}'.format(
                              (b1 & 0x0f), (b2 >> 4) ),        # 8ts3 XOR vt, vs
    0x04 : lambda b1, b2: 'ADD V{:1X}, V{:1X}'.format(
                              (b1 & 0x0f), (b2 >> 4) ),        # 8ts4 ADD vt, vs
    0x05 : lambda b1, b2: 'SUB V{:1X}, V{:1X}'.format(
                              (b1 & 0x0f), (b2 >> 4) ),        # 8ts5 SUB vt, vs
    0x06 : lambda b1, b2: 'SHR V{:1X}, V{:1X}'.format(
                              (b1 & 0x0f), (b2 >> 4) ),        # 8t06 SHR vt
    0x07 : lambda b1, b2: 'SUBN V{:1X}, V{:1X}'.format(
                              (b1 & 0x0f), (b2 >> 4) ),        # 8ts7 SUBN vt, vs
    0x0E : lambda b1, b2: 'SHL V{:1X}, V{:1X}'.format(
                              (b1 & 0x0f), (b2 >> 4) )         # 8t0E SHL vt
    }

def disasm_8xxx( b1:int, b2:int ) -> str :
    op = b2 & 0x0f
    if op in decode_8xxx :
        return decode_8xxx[ op ]( b1, b2 )
    return ''

'''
Ex9E : skip if key vx is down
ExA1 : skip if key vx is up
'''
def disasm_Exxx ( b1: int, b2:int ) -> str :
    if b2 == 0x9E :
        return 'SKP V{:1X}'.format( b1 & 0x0f )
    elif b2 == 0xA1 :
        return 'SKNP V{:1X}'.format( b1 & 0x0f )
    else :
        return ''


decode_Fxxx = {
    0x07 : lambda b1, b2 : 'LD V{:1X}, DT'.format( b1 & 0x0f ), # Ft07 LD Vt, DT
    0x0A : lambda b1, b2 : 'LD V{:1X}, K'.format( b1 & 0x0f ),  # Ft0A LD Vt, K
    0x15 : lambda b1, b2 : 'LD DT, V{:1X}'.format( b1 & 0x0f ), # Fs15 LD DT, Vs
    0x18 : lambda b1, b2 : 'LD ST, V{:1X}'.format( b1 & 0x0f ), # Fs18 LD ST, Vs
    0x1E : lambda b1, b2 : 'ADD I, V{:1X}'.format( b1 & 0x0f ), # Fs1E ADD I, Vs
    0x29 : lambda b1, b2 : 'LDC I, V{:1X}'.format( b1 & 0x0f ), # Fs29 LDC I, Vs
    0x30 : lambda b1, b2 : 'LDH I, V{:1X}'.format( b1 & 0x0f ), # Fs30 LDH I, Vs
    0x33 : lambda b1, b2 : 'STD V{:1X}'.format( b1 & 0x0f ),    # Fs33 STD Vs
    0x55 : lambda b1, b2 : 'STM V{:1X}'.format( b1 & 0x0f ),    # Fx55 STM Vx
    0x65 : lambda b1, b2 : 'LDM V{:1X}'.format( b1 & 0x0f )     # Fx65 LDM v0, Vx
    }

def disasm_Fxxx( b1:int, b2:int ) ->str :
    if b2 in decode_Fxxx :
        return decode_Fxxx[ b2 ]( b1, b2 )
    return ''



decode_first_byte = {
    0x00 : disasm_00xx, # decode several instructions
           # decode 1xxx, JUMP xxx
    0x10 : lambda b1, b2 : 'JP LBL{:04X}'.format( add_label( b1, b2 ) ),
           # decode 2xxx, CALL xxx
    0x20 : lambda b1, b2 : 'CALL LBL{:04X}'.format( add_label( b1, b2 ) ),
           # decode 3vxx, SE v, xx
    0x30 : lambda b1, b2 : 'SE V{:1X}, #{:02X}'.format( (b1 & 0x0f), b2 ),
           # decode 4vxx, SNE v, xx
    0x40 : lambda b1, b2 : 'SNE V{:1X}, #{:02X}'.format( (b1 & 0x0f), b2 ),
           # decode 5vw0, SE v, w -- ensure last digit 0
    0x50 : lambda b1, b2 : 'SE V{:1X}, V{:1X}'.format( (b1 & 0x0f), (b2 >> 4) ) \
                            if (0 == b2 & 0x0f) else '',
           # decode 6vxx, LD v, xx
    0x60 : lambda b1, b2 : 'LD V{:1X}, #{:02X}'.format( (b1 & 0x0f), b2 ),
           # decode 7vxx, ADD v, xx
    0x70 : lambda b1, b2 : 'ADD V{:1X}, #{:02X}'.format( (b1 & 0x0f), b2 ),
           # decode logical instructions
    0x80 : disasm_8xxx,
           # decode 9vw0, SKNE v, w -- ensure last digit 0
    0x90 : lambda b1, b2 : 'SNE V{:1X}, V{:1X}'.format( (b1 & 0x0f), (b2 >> 4) ) \
                            if (0 == b2 & 0x0f) else '',
           # decode Axxx, LOAD I, xxx
    0xA0 : lambda b1, b2 : 'LD I, LBL{:04X}'.format( add_label( b1, b2 ) ),
           # decode Bxxx, JUMP V0, xxx
    0xB0 : lambda b1, b2 : 'JP V0, LBL{:04X}'.format( add_label( b1, b2 ) ),
           # decode Ctbb, RND Vt, bb
    0xC0 : lambda b1, b2 : 'RND V{:1X}, #{:02X}'.format( (b1 & 0x0f), b2 ),
           # decode Dxxx, DRAW Vx, Vy, N
    0xD0 : lambda b1, b2 : 'DRAW V{:1X}, V{:1X}, {}'.format( (b1 & 0x0f), (b2 >> 4), (b2 & 0x0f ) ),
    0xE0 : disasm_Exxx, # decode two keypad tests
    0xF0 : disasm_Fxxx  # decode various special-reg ops
    }




def disassemble( byte_string : bytes ) -> str :
    global TARGET_SET
    TARGET_SET = set()

    '''
    If byte_string is longer than 3,584 the this cannot be a valid S/CHIP
    binary because that's all the memory the machine had. Set that limit so
    we can be sure that we have at most ~3500 statements to produce.
    '''
    if len(byte_string) > 3584 :
        return 'Input too long - not an S/CHIP-8 program.'

    '''
    For a start, convert the byte-string into a list of ints. This takes a
    bit of time and memory, but the list is much easier to index, and faster,
    too, than doing slices on the byte-string.
    '''
    b_list = [ b for b in byte_string ]

    '''
    We will build up our output as a dict in which the key is the PC
    and the value is the statement for that PC.
    '''
    output_text = dict()
    TARGET_SET = set()

    '''
    We will usually consume two bytes at a time, but sometimes only one. I
    don't see an alternative to a C-like loop. Set the limit one byte low so
    that we don't run off the end trying to access (b1, b2).
    '''
    PC = 0
    limit = len( b_list ) - 1
    while PC < limit : # while at least two bytes remain,

        address = PC + 0x0200
        b1 = b_list[ PC ]
        b2 = b_list[ PC+1 ]
        statement = decode_first_byte[ b1 & 0xf0 ] ( b1, b2 )
        if statement : # was not null,
            '''
            We successfully decoded b1, b2 into an instruction.
            Add a tab at the front and a comment with its hex value
            at the back.
            '''
            statement = '\t' + statement + ' ; {:02X}{:02X}'.format( b1, b2 )
            '''
            Stow it keyed by its logical address and increment PC.
            '''
            PC += 2

        else :
            '''
            We couldn't make sense of b1, b2. Make a DB of b1 and
            advance PC by only one.
            '''
            statement = '\tDB #{:02X}'.format( b1 )
            PC += 1
        output_text[ address ] = statement
    '''
    That's disassembly, folks. Terse, eh? Oh, except we might not have
    done the last byte of the list.
    '''
    if PC < len( b_list ) :
        address = PC + 0x0200
        output_text[ address ] = '\tDB #{:02X}'.format( b_list[-1] )

    '''
    go through the addresses of TARGET_SET in sequence, adding or inserting labels
    of the form "LBL0xxx:" at appropriate points in output_text.

    It would be nice to be assured that every label matched to a statement
    but we can't be sure of that. Walk the list inserting a label where there
    is a match to a statement, or EQU where there is not.

    Make a list of the known statement addresses, adding a sentinel to keep us
    from running off the end. Output of sorted() is a list -- not a generator as
    I supposed it might be.
    '''
    statement_addresses = sorted( output_text.keys() ) + [10000]
    unmatched_addresses = []
    i = 0
    for target in sorted( TARGET_SET ) :

        while target > statement_addresses[i] : i += 1
        '''
        target is <= statement_addresses[i]
        '''
        if target == statement_addresses[i] :
            '''
            The target PC matches the PC of a statement. Insert the LBL0xxx:
            into the statement in place of the tab.
            '''
            statement = output_text[ target ]
            output_text[ target ] = 'LBL{:04X}: '.format( target ) + statement[1:]
        else :
            '''
            The target PC does not match (it is not equal nor greater than
            the current statement's PC). Insert it as an equate statement at
            the head of the file. Use -target as the key. Save -target in the
            list of unmatched addresses for use below.
            '''
            output_text[ -target ] = 'LBL{0:04X} EQU #{0:04x} ; unmatched label'.format( target )
            unmatched_addresses.append( -target )
    '''
    Make all the statement strings into a list in PC order, then join the
    list on newlines to make a document load.

    statement_addresses is already a list of the keys to output_text (plus
    that sentinel), and unmatched_addresses is a list of the needed EQU
    statements. Combine them to get the list of all keys for which there are
    statements in output_text.
    '''
    output = '\n'.join(
        [ output_text[pc] for pc in ( unmatched_addresses + statement_addresses[:-1] ) ]
    )

    return output

# bit o' unit testing here

if __name__ == '__main__' :
    from binasm import *

    print( disassemble( bytes( binasm( P3 ) ) ) )

