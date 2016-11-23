__license__ = '''
 License (GP: lambda S : [3.0) :
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

    CHIP-8 IDE ASSEMBLY PHASE TWO

This is a sub-module of the source.py module, which implements the source
editor window.

The code here implements the final assembly of the Statement objects
into binary values, and the disassembly of a byte string into legal assembler.

The assemble() function is called from source.py when the Check or Load
button is clicked. The user should not, but might, click Check while there
are still syntax errors to fix. Other errors may be found as we evaluate
expressions.

If no errors are found, we return a list of ints that represents the binary
value of this code, from emulated memory location 0x0200 up through the
last non-zero byte.

When errors are found update the Statement objects as necessary (setting
the S.expr_error flag) and return None. The Check handler then takes appropriate
action to inform the user.

'''
import logging

__all__ = [ 'assemble' ]

'''
Import the Statement class.
'''
from statement_class import Statement

'''

Symbol table:

On our first pass through the statements we note defined names in this dict.
The LOOKUP() function returns the value of a name if it is defined,
or it raises an IndexError with an appropriate message.

'''

SYMBOLS = dict()

def LOOKUP( name:str ) -> int :
    try :
        return SYMBOLS[ name ]
    except KeyError as K :
        raise IndexError( 'Symbol {} is undefined'.format( str(K) ) )

'''
About expressions: Certain opcodes and all Directives have expression
operands.

The phase_one check ensures that there is the appropriate number of
expressions. However we do not know if the expressions will evaluate to
appropriate values.

When an expression should be a byte, we check that it is positive and in
0..255 and issue an error if not. Similarly, an address needs to fall in
0x0200..0x0FFF, and a nybble in 0..15. (We allow an EQU to evaluate to any
integer, because there is no telling how that name will be used in an
expression.)

This might seem too restrictive, for example one might say we should allow
"LD V5,-2" to put 0xFE in V5. But if that is the intent, the user should code
it that way (LD V5, #FE).

Anyway, it is possible that an expression using names could end up with an
inappropriate value, not because the user is being clever and relying on
binary arithmetic, but because of a coding error many statements distant from
the expression, and strict application of the limits will help the user find
such a bug faster.

The following function evaluates an expression from S -- in the form of a
Python code-object -- for value in a certain range. It throws an exception
with a helpful message in case of an error. Possible exceptions:
  IndexError( "Symbol X is undefined") from LOOKUP
  ZeroDivisionError( "division by zero" ) from eval
  Something else? from eval
  ValueError( "Inappropriate expression value N" )

'''

def check_value( code_object, low:int, high:int ) -> int :
    global LOOKUP
    value = eval( code_object, globals() )
    value = int( value )
    if value < low or value > high :
        raise ValueError('Inappropriate expression value {}'.format( value ) )
    return value

'''
The following code implements all opcodes and directives except DS, EQU and ORG.

Instructions that do not involve expression evaluation can be assembled by a
simple lambda expression on the Statement object, returning a list of 2 bytes.

The remaining instructions fit one of four patterns:

opcode, reg, byte

3sKK Skip next instruction if Vs == KK
4sKK Skip next instruction if Vs != KK
CtKK Let Vt = Random Byte (KK =Mask)
6tKK Let Vt = KK
7tKK Let Vt = VX + KK

opcode, address

1MMM Go to OMMM
BMMM Go to OMMM +VO
2MMM Do subroutine at OMMM (must end with OOEE)
AMMM Let I = 0MMM

opcode, nybble

(00CN) 00CN scroll down N lines

opcode, reg, reg, nybble

(DXYN) DXYN Show N-byte pattern from MI at VX-VY coordinates.

The following functions implement those patterns.

Note they do not trap exceptions. Exceptions are allowed to unwind all the
way up the assembly() statement that calls these functions.

'''
from typing import List

def op_reg_byte( opcode: int, S : Statement ) -> List[int] :
    byte_0 = opcode | S.reg_1
    byte_1 = check_value( S.expressions[0], 0, 255 )
    return [byte_0, byte_1]

def op_addr( opcode : int, S : Statement ) -> List[int] :
    address = check_value( S.expressions[0], 0, 4095 )
    byte_0 = opcode | ( address >> 8 )
    byte_1 = address & 0x00FF
    return [byte_0, byte_1]

def op_nybble( opcode: int, S : Statement ) -> List[int] :
    nybble = check_value( S.expressions[0], 0, 15 )
    byte_0 = opcode >> 8
    byte_1 = ( opcode | nybble ) & 0xFF
    return [byte_0, byte_1]

def op_reg_reg_nybble( opcode: int, S: Statement ) -> List[int] :
    byte_0 = opcode | S.reg_1
    nybble = check_value( S.expressions[0], 0, 15 )
    byte_1 = ( S.reg_2 << 4 ) | int( nybble )
    return [byte_0, byte_1]

'''
The directives need individual treatment. These three directives are
like opcodes: they evaluate expressions and return a list of bytes.
'''

def directive_da( S:Statement ) -> List[int] :
    '''
    phase_one ensures the argument of DA is a single string which it
    encodes as bytes("...",encoding="ASCII"). So, it becomes quite easy
    to process. Probably no error can result except, maybe, if they
    snuck a non-ASCII char into the string, encoding error.
    '''
    byte_list = list( eval( S.expressions[0], globals() ) )
    return byte_list

def directive_db( S: Statement ) -> List[int] :
    '''
    phase_one collects the zero or more expressions in S.expressions.
    Use check_value() to make sure they are all valid bytes and
    everything is defined.
    '''
    byte_list = []
    for code_object in S.expressions :
        byte_list.append( check_value( code_object, 0, 255 ) )
    return byte_list

def directive_dw( S:  Statement ) -> List[int] :
    '''
    phase_one collects the zero or more expressions in S.expressions. Use
    check_value() to make sure they are all valid. Allow them to range
    0..65535. We cannot be certain they will be used as addresses (and the
    emulator will barf on an address out of range anyway).
    '''
    byte_list = []
    for code_object in S.expressions :
        word = check_value( code_object, 0, 65535 )
        byte_list.append( word >> 8 )
        byte_list.append( word & 0xFF )
    return byte_list

'''

In the following dict, the instruction type from Statement.form is the key,
and the value is a lambda that receives the argument S as a Statement object,
and returns a list of byte values.

Note when a special register (I, DT, DS, K) is the first operand, the
source V-reg comes from S.reg_2.

'''
opcode_dict = {
    'ADDI' : lambda S : [ 0xF0 + S.reg_2, 0x1E ] ,               # Fs1E ADD I, Vs
    'ADDR' : lambda S : [ 0x80 + S.reg_1, (S.reg_2 << 4) | 0x04 ], # 8ts4 ADD Vt, Vs
    'AND'  : lambda S : [ 0x80 + S.reg_1, (S.reg_2 << 4) | 0x02 ], # 8ts2 AND Vt, Vs
    'CLS'  : lambda S : [ 0x00, 0xE0 ],                          # 00E0 CLEAR
    'EXIT' : lambda S : [ 0x00, 0xFD ],                          # 00FD EXIT
    'HIGH' : lambda S : [ 0x00, 0xFF ],                          # 00FF HIGH
    'LDC'  : lambda S : [ 0xF0 + S.reg_2, 0x29 ],                # Fs29 LDC I, Vs
    'LDH'  : lambda S : [ 0xF0 + S.reg_2, 0x30 ],                # Fs30 LDH I, Vs
    'LDK'  : lambda S : [ 0xF0 + S.reg_1, 0x0A ],                # Ft0A LD Vt, K
    'LDM'  : lambda S : [ 0xF0 + S.reg_1, 0x65 ],                # Ft65 LDM Vt
    'LDRR' : lambda S : [ 0x80 + S.reg_1, (S.reg_2 << 4) | 0x00 ], # 8ts0 LD Vt, Vs
    'LDRT' : lambda S : [ 0xF0 + S.reg_1, 0x07 ],                # Ft07 LD Vt, DT
    'LDSR' : lambda S : [ 0xF0 + S.reg_2, 0x18 ],                # Fs18 LD ST, Vs
    'LDTR' : lambda S : [ 0xF0 + S.reg_2, 0x15 ],                # Fs15 LD DT, Vs
    'LOW'  : lambda S : [ 0x00, 0xFE ],                          # 00FE LOW
    'OR'   : lambda S : [ 0x80 + S.reg_1, (S.reg_2 << 4) | 0x01 ], # 8ts1 OR Vt, Vs
    'RET'  : lambda S : [ 0x00, 0xEE ],                          # 00EE RET
    'SCL'  : lambda S : [ 0x00, 0xFC ],                          # 00FC SCL
    'SCR'  : lambda S : [ 0x00, 0xFB ],                          # 00FB SCR
    'SER'  : lambda S : [ 0x50 + S.reg_1, (S.reg_2 << 4) | 0x00 ], # 5XY0 SE Vx, Vy
    'SHR'  : lambda S : [ 0x80 + S.reg_1, (S.reg_2 << 4) | 0x06 ], # 8ts6 SHR Vt, Vs
    'SHL'  : lambda S : [ 0x80 + S.reg_1, (S.reg_2 << 4) | 0x0E ], # 8tsE SHL Vt, Vs
    'SKP'  : lambda S : [ 0xE0 + S.reg_1, 0x9E ],                # EX9E SKP Vx
    'SKNP' : lambda S : [ 0xE0 + S.reg_1, 0xA1 ],                # EXA1 SKNP Vx
    'SNER' : lambda S : [ 0x90 + S.reg_1, (S.reg_2 << 4) | 0x00 ], # 9XY0 SNE Vx, Vy
    'STD'  : lambda S : [ 0xF0 + S.reg_1, 0x33 ],                # FX33 STD Vx
    'STM'  : lambda S : [ 0xF0 + S.reg_1, 0x55 ],                # FX55 STM Vx
    'SUB'  : lambda S : [ 0x80 + S.reg_1, (S.reg_2 << 4) | 0x05 ], # 8ts5 SUB Vt, Vs
    'SUBN' : lambda S : [ 0x80 + S.reg_1, (S.reg_2 << 4) | 0x07 ], # 8XY7 SUBN Vt, Vs
    'XOR'  : lambda S : [ 0x80 + S.reg_1, (S.reg_2 << 4) | 0x03 ], # 8ts3 XOR Vt, Vs
    'SEB'   : lambda S: op_reg_byte( 0x30, S ),                  # 3sbb SE Vs, BB
    'SNEB'  : lambda S: op_reg_byte( 0x40, S ),                  # 4sbb SNE Vs, BB
    'LDRB'  : lambda S: op_reg_byte( 0x60, S ),                  # 6tbb LD Vt, BB
    'ADDB'  : lambda S: op_reg_byte( 0x70, S ),                  # 7tbb ADD Vt, BB
    'RND'   : lambda S: op_reg_byte( 0xC0, S ),                  # Ctmm RND Vt, mm
    'JPADR' : lambda S: op_addr( 0x10, S ),                      # 1aaa JP aaa
    'CALL'  : lambda S: op_addr( 0x20, S ),                      # 2aaa CALL aaa
    'LDI'   : lambda S: op_addr( 0xA0, S ),                      # Aaaa LD I, aaa
    'JPXADR': lambda S: op_addr( 0xB0, S ),                      # Baaa JP V0, aaa
    'DRAW'  : lambda S: op_reg_reg_nybble( 0xD0, S ),            # Dxyn DRAW Vx, Vy, n
    'SCD'   : lambda S: op_nybble( 0x00C0, S ),                  # 00Cn SCD n
    'DA'    : lambda S: directive_da( S ),                       #      DA string
    'DB'    : lambda S: directive_db( S ),                       #      DB expr [,...]
    'DW'    : lambda S: directive_dw( S )                        #      DW expr [,...]
    }




'''

    The Forward-reference problem!

We do want to support forward references, e.g.

    CALL DO_SUB
    ...
DO_SUB: ...

The problem is that we cannot know the value of any label such as DO_SUB, or
keep an accurate symbol table, while editing is going on. As long as the user
is free to change any statements while editing, the user can:

* Delete the CALL line, removing what might be the only reference to DO_SUB
from the program.

* Insert or delete any number of statements between the CALL and the label,
changing the value of DO_SUB.

* Delete the DO_SUB line and replace it at point in the program above or
below the CALL at any future time.

* Enter a duplicate DO_SUB label, then maybe go back to delete one.

Note especially in the case of deleting, we get no signal that a delete has
occurred. The QSyntaxHighlighter is called to validate new and modified
lines, but there is no call from the editor when a line (or lines) are
deleted.

For these reasons, we cannot keep track of symbols at edit time. Only when
the user calls for a full assembly by clicking "Check" and "Load"
can we be sure no editing is happening at least for that time.

Then we can do the classic two-pass assembly: on pass 1, note the values of
all labels based on the known byte-count generated by all instructions. Then
on pass 2, actually evaluate all expressions and complete the assembly.

That's fine except for...

    The ORG problem!

ORG says, move the assembler's output pointer to a different address. The
problem is, that potentially changes the value of all following labels.
Consider:

    HERE: ; evaluates to 0x0300, say
       ORG HERE + #20 ; this is OK
       ORG BUF + #80 ; this is ambiguous
    BUF DS #80

At what PC should BUF assemble? An ORG whose expression depends on a forward
reference is inherently indeterminate.

DS has a similar problem when its expression refers to labels defined after
the DS statement. The size of the reserved space depends on the location of
the label, which depends on the size of the reserved space.

For these reasons, we decree that neither DS nor ORG may use forward
references. Their expressions must evaluate correctly when they are seen in
the first pass, or they are in error.

EQU is related in that its expression might refer to some label defined below
the EQU. However this would be a valid use, for example a jump table to be
reached via the indexed jump:

    KEY0_OFFSET EQU K0_ENTRY - TABLE
    KEY1_OFFSET EQU K1_ENTRY - TABLE
    ...
        LD v0, KEY1_OFFSET
        JP v0, TABLE

    TABLE: ;
    K0_ENTRY: ... code for K0
           ...
    K1_ENTRY: ... code for K1
           ...

(That's overcomplicated of course; you could just as well put the expression
K0_ENTRY-TABLE in the LD v0 instruction, where it would be uncontroversial.)

You might think that EQU is benign in that it doesn't affect the PC
the way ORG and DS do. But names defined by EQU can be used in an ORG
or DS expression, and that would potentially sneak forward references into
ORG or DS again.

So I am giving EQU statements special treatment. If an EQU expression
evaluates correctly in the first pass, fine. Set its S.defined_value and move
on. If it does not evaluate because of an undefined name, save that text
block on a list. At the end of the first pass, when all statement labels are
resolved, re-try the EQU's in the list. If they depended only on forward
references, they will now evaluate.

However, ORG and DS are processed during the first pass, and their
expressions must resolve at that time. If they fail because a name is
undefined -- which could be either a forward label or an EQU that has not
been resolved because it depends on a forward label -- they are in error.

These rules permit code like this, a reasonable use of EQU, DS and ORG:

    BSIZE = 128
    BUFR: DS BSIZE
          ORG BUFR
          DB ....
          ORG BUFR+32
          DB ...
          ORG BUFR+BSIZE


The argument to assemble() is the first QTextBlock of the source document,
which can be used as the basis of an iterator over lines in sequence.
'''

from PyQt5.QtGui import QTextBlock

def assemble( first_text_block: QTextBlock ) -> List[int] :
    global SYMBOLS, LOOKUP

    '''
    Iterate over all the text blocks. Define all labels. Count
    any text_errors. Implement EQU, ORG and DS.

    Note that the PC starts at 0x0200; this is a historical convention. The
    original CHIP-8 had the actual emulator code below that address, so
    programs could not use it. Now we store font patterns there and still do
    not allow its use.
    '''
    SYMBOLS = dict()
    text_errors = 0
    expr_errors = 0
    PC = 0x0200
    list_of_deferred_equates = []
    this_block = first_text_block
    while this_block.isValid() :
        U = this_block.userData()
        S = U.statement
        '''
        If it is an uncorrected syntax error, just count it.
        '''
        if S.text_error :
            text_errors += 1
        else :
            '''
            Clear the Statement fields used by assembly.
            '''
            S.init_assembly()
            '''
            If this defines a name, try to define that name.
            '''
            if S.defined_name : # is not null,
                '''
                If the name is already in the symbol table, we have a
                duplicate definition error.
                '''
                if S.defined_name in SYMBOLS :
                    S.expr_error = True
                    expr_errors += 1
                    S.error_pos = 0
                    S.error_msg = '{} defined multiple times'.format(S.defined_name)
                else :
                    '''
                    If the name is a simple label, define it with the
                    current PC as its value.
                    '''
                    if S.form != 'EQU' :
                        SYMBOLS[ S.defined_name ] = PC
                    else:
                        '''
                        An equate: try to evaluate its expression and if that
                        works, bonzer, define it. If it fails for IndexError,
                        save it to try again later. Any other failure, quit.
                        '''
                        try :
                            value = check_value( S.expressions[0], 0, 65535 )
                            SYMBOLS[ S.defined_name ] = value
                        except IndexError as I :
                            list_of_deferred_equates.append( this_block )
                        except Exception as E :
                            S.expr_error = True
                            expr_errors += 1
                            S.error_pos = 0
                            S.error_msg = str(E)
            # endif S.defined_name
            '''
            phase_one leaves S.next_pc an integer except for ORG and DS.
            '''
            if S.next_pc is not None :
                '''
                For all normal statements, just advance the PC by S.next_pc.
                '''
                PC += S.next_pc
            elif S.form == 'DS' :
                '''
                For DS, evaluate its expression, making sure it does not
                push PC off the end of memory. Then just advance PC over
                the reserved space.
                '''
                try :
                    value = check_value( S.expressions[0], 0, 4096-PC )
                    S.next_pc = value
                    PC += value
                except Exception as E :
                    S.expr_error = True
                    expr_errors += 1
                    S.error_pos = 0
                    S.error_msg = str(E)
            elif S.form == 'ORG' :
                '''
                For ORG, evaluate the expression and make sure it falls in
                the valid range for memory addresses. Then set PC from it.
                '''
                try :
                    value = check_value( S.expressions[0], 0x0200, 0xFFF )
                    S.next_pc = value
                    PC = value
                except Exception as E :
                    S.expr_error = True
                    expr_errors += 1
                    S.error_pos = 0
                    S.error_msg = str(E)
            else :
                s.expr_error = True
                expr_errors += 1
                S.error_pos = 0
                S.error_msg = 'assembler bug S.form{} but S.next_pc is None'.format(S.form)
                logging.error(S.error_msg)

        # endif S.text_error
        '''
        Make sure the PC is still in range. If not, tag the current statement
        for the error, and quit the loop.
        '''
        if PC > 4095 :
            S.expr_error = True
            expr_errors += 1
            S.error_pos = 0
            S.error_msg = 'Assembly too large, off the end of memory'
            break
        '''
        Advance to the next text line.
        '''
        this_block = this_block.next()
    # end while this_block.isValid()
    '''
    Pass one is complete. If no errors were noted, try to process any
    remaining EQU statements. Do them in reversed order, so that if an
    earlier one depends on a later one, it will resolve.
    '''
    if 0 == ( expr_errors + text_errors ) :
        for this_block in reversed( list_of_deferred_equates ) :
            U = this_block.userData()
            S = U.statement
            try :
                value = check_value( S.expressions[0], 0, 65535 )
                SYMBOLS[ S.defined_name ] = value
            except Exception as E :
                S.expr_error = True
                expr_errors += 1
                S.error_pos = 0
                S.error_msg = str(E)

    '''
    If we have noted any errors in the first pass, just bail returning
    a list [-1, text-errors, expression-errors] to our caller. (The
    initial negative shows that it is not a valid memory load.) This
    makes the CHECK routine's work a little easier.
    '''
    if ( expr_errors + text_errors ) :
        return [ -1, text_errors, expr_errors ]

    '''
    Iterate once more over all text blocks. This time, generate their byte
    values and store them in a big array of bytes which we will return.

    It is still possible to get errors because it is only now that we try to
    evaluate expressions in opcodes. When exceptions occur in the subordinate
    functions (the ones called from opcode_dict) they bubble up to here. We
    mark the statement but continue. In general we want to document as many
    errors as possible, to save the user the trouble of correcting errors one
    at a time.
    '''
    memory_image = [0] * 4096
    PC = 0x200
    top_address = 0
    this_block = first_text_block
    while this_block.isValid() :
        U = this_block.userData()
        S = U.statement
        if S.form in opcode_dict :
            try :
                byte_list = opcode_dict[ S.form ]( S )
                memory_image[ PC : PC + len( byte_list ) ] = byte_list
                S.value = list( byte_list )
                S.PC = PC
            except Exception as E :
                expr_errors += 1
                S.expr_error = True
                S.error_pos = 0
                S.error_msg = str( E )
            PC += S.next_pc
        else :
            '''
            The only statements not in opcode_dict are DS, EQU and ORG
            and null (comment-only) lines. Increment PC appropriately.
            '''
            if S.form == 'ORG' :
                PC = S.next_pc
            elif S.form == 'DS' :
                PC += S.next_pc
            elif S.form == 'EQU' :
                pass
            elif S.form == '' :
                pass
            else :
                expr_errors += 1
                S.expr_error = True
                S.error_pos = 0
                S.error_msg = 'assembler error S.form{} unexpected'.format(S.form)
                logging.error( S.error_msg )

        # endif S.form in opcode_dict
        top_address = max( top_address, PC )
        this_block = this_block.next()
    # end loop over statements

    '''
    If we found any errors on that pass, return [-1, yadda yadda]
    '''
    if expr_errors :
        return [ -1, text_errors, expr_errors ]

    '''
    Return the slice of the memory image from 0x0200 through the last
    byte generated.
    '''
    return memory_image[ 0x0200 : top_address ]
