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
    <http:# www.gnu.org/licenses/>.
'''
__version__ = "1.0.0"
__author__  = "David Cortesi"
__copyright__ = "Copyright 2016 David Cortesi"
__maintainer__ = "David Cortesi"
__email__ = "davecortesi@gmail.com"

import display

'''
Define the names that comprise the public API to this module. No other names
will be visible to code that imports this module.
'''

__all__ = [
    'R',            # enumerated register indices
    'REGS',         # dict of regs, keyed by R.
    'MEMORY',       # emulated memory, one int per emulated byte
    'CALL_STACK',   # emulated call stack
    'MEMORY_CHANGE',# flag set when memory modified
    'reset_vm',     # clear memory, regs, call stack
    'step',         # execute one emulated instruction
    'tick',         # note passage of 1/60th second
    'bp_add',       # add breakpoint
    'bp_rem',       # remove breakpoint
    'bp_clear',     # clear breakpoints
    'reset_notify', # register a callback for memory resest
    'initialize',   # do some startup TBS
    'shutdown'      # do some shutdown TBS
]

'''
Global REGS is a dict containing the registers of the emulated machine.
The dict is keyed by an IntEnum R naming the registers, thus R.I is the
I-register's index in REGS.

We do something that is not recommended for the Enum class: we ASSUME
a relation between integers 0..15 and the names v0..vF. This is for speed,
so we can access a reg by REGS[(INST & 0x0F00)>>8] with no further decoding.

The memory module imports R and REGS directly (from chip8 import R, etc)
for easier access.
'''
from enum import IntEnum

class R( IntEnum ) :
    v0 = 0 # the 16 one-byte "variable" regs
    v1 = 1
    v2 = 2
    v3 = 3
    v4 = 4
    v5 = 5
    v6 = 6
    v7 = 7
    v8 = 8
    v9 = 9
    vA = 10
    vB = 11
    vC = 12
    vD = 13
    vE = 14
    vF = 15
    I = 16 # the I-reg addresses memory
    T = 17 # the sound timer
    S = 18 # the time timer
    P = 19 # the PC

REGS = {} # type Dict[ R, int ]

'''
MEMORY is the 4096-byte emulated memory, stored as a list of ints.
'''

MEMORY = [] # type List[int]

'''
MEMORY_CHANGED is a flag set during the only two instructions that can
actually modify memory, STM and STD. The Memory module uses this to know
when to update the memory display table.
'''
MEMORY_CHANGED = False

'''
CALL_STACK is a 12-entry list of return addresses. Refer to the COSMAC VIP
manual (PDF in extras folder) page 36: the original call stack had 12 levels.
'''

MAX_CALL_DEPTH = 12
CALL_STACK = [] # type List[int]

'''
Define the two sets of font sprites. This is copied from Brad Miller's
schip.cpp code because I'm really lazy.
'''
FONT_5x4 = [
    0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
    0x20, 0x60, 0x20, 0x20, 0x70, # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
    0x90, 0x90, 0xF0, 0x10, 0x10, # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
    0xF0, 0x10, 0x20, 0x40, 0x40, # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90, # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
    0xF0, 0x80, 0x80, 0x80, 0xF0, # C
    0xE0, 0x90, 0x90, 0x90, 0xE0, # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
    0xF0, 0x80, 0xF0, 0x80, 0x80  # F
]

FONT_8x10 = [
    0x00, 0x3C, 0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x3C, 0x00, # 0
    0x00, 0x08, 0x38, 0x08, 0x08, 0x08, 0x08, 0x08, 0x3E, 0x00, # 1
    0x00, 0x38, 0x44, 0x04, 0x08, 0x10, 0x20, 0x44, 0x7C, 0x00, # 2
    0x00, 0x38, 0x44, 0x04, 0x18, 0x04, 0x04, 0x44, 0x38, 0x00, # 3
    0x00, 0x0C, 0x14, 0x24, 0x24, 0x7E, 0x04, 0x04, 0x0E, 0x00, # 4
    0x00, 0x3E, 0x20, 0x20, 0x3C, 0x02, 0x02, 0x42, 0x3C, 0x00, # 5
    0x00, 0x0E, 0x10, 0x20, 0x3C, 0x22, 0x22, 0x22, 0x1C, 0x00, # 6
    0x00, 0x7E, 0x42, 0x02, 0x04, 0x04, 0x08, 0x08, 0x08, 0x00, # 7
    0x00, 0x3C, 0x42, 0x42, 0x3C, 0x42, 0x42, 0x42, 0x3C, 0x00, # 8
    0x00, 0x3C, 0x42, 0x42, 0x42, 0x3E, 0x02, 0x04, 0x78, 0x00, # 9
    0x00, 0x18, 0x08, 0x14, 0x14, 0x14, 0x1C, 0x22, 0x77, 0x00, # A
    0x00, 0x7C, 0x22, 0x22, 0x3C, 0x22, 0x22, 0x22, 0x7C, 0x00, # B
    0x00, 0x1E, 0x22, 0x40, 0x40, 0x40, 0x40, 0x22, 0x1C, 0x00, # C
    0x00, 0x78, 0x24, 0x22, 0x22, 0x22, 0x22, 0x24, 0x78, 0x00, # D
    0x00, 0x7E, 0x22, 0x28, 0x38, 0x28, 0x20, 0x22, 0x7E, 0x00, # E
    0x00, 0x7E, 0x22, 0x28, 0x38, 0x28, 0x20, 0x20, 0x70, 0x00  # F
]

'''
Store a list of 0 or more callables to be called when the emulated
machine is reset. In case, you know, you need to clear something.
'''
from typing import Callable

NOTIFY_LIST = [] # type List[Callable]

def reset_notify( callback : Callable ) -> None :
    global NOTIFY_LIST
    NOTIFY_LIST.append( callback )

'''
Reset the virtual machine to starting condition:

* Call stack cleared
* Breakpoints cleared
* Regs v0..vF, I, T and S cleared
* PC set to 0x0200
* Display set to CHIP-8 mode
* Sound turned off
* Memory cleared
* MEMORY_CHANGED flag set True
* 5x4 font sprites loaded in 0x0000..0x004F (5*16 == 80 == 0x50)
* 10x8 SCHIP font sprites loaded in 0x0050..0x00EF (10*16 == 160 == 0xA0)
* Optionally, memory from 0x0200 loaded with a program
* If one is registered, call a callback (e.g. memory.py)

A note on font sprites. Refer to the COSMAC VIP manual page 37 (PDF in the
"extras"). The CHIP-8 font sprites were located in ROM at 0x8110 (and
cleverly overlapped to use less space). However (page 36) memory from
0x0000..0x01FF was reserved for the actual code of the CHIP-8 interpreter, so
it was off-limits to the user program. Checking the code of two other
emulators it seems to be customary to locate the font sprites in
that space below 0x0200.

'''

from typing import List

def reset_vm( memload : List[int] = None ) -> None :

    global MEMORY, MEMORY_CHANGED, REGS, CALL_STACK

    '''
    Clear the call stack.
    '''
    CALL_STACK = []

    '''
    Clear the breakpoints
    '''
    bp_clear()

    '''
    Clear all machine regs to default values
    '''
    REGS = { r:0 for r in R }
    REGS[R.P] = 0x0200

    '''
    Reset the display to CHIP-8 mode and sound off
    '''
    display.set_mode( schip= False ) # also clears display
    display.sound( on= False )

    '''
    Clear memory, load font sprites
    '''
    MEMORY = [0] * 4096
    MEMORY[ 0:80 ] = FONT_5x4
    MEMORY[ 80:240 ] = FONT_8x10
    MEMORY_CHANGED = True

    '''
    If a memload is supplied, it is a list of ints which are the
    byte-by-byte contents to load into memory from 0x0200. The Source module
    passes the current assembled program, or it could be a unit test.
    '''
    if memload is not None :
        assert len( memload ) <= (4096-0x0200)
        MEMORY[ 0x0200 : 0x01FF + len( memload ) ] = memload

    '''
    If anyone cares, let them know we are changed.
    '''
    for callback in NOTIFY_LIST :
        try : # trust nobody
            callback( )
        except Exception as E:
            pass

'''
Manage the breakpoint list. The Source module calls these entries as the user
sets or clears breakpoints on source lines.
'''
BREAKPOINTS = [] # type List[int]

def bp_clear( ) -> None :
    global BREAKPOINTS
    BREAKPOINTS = []

def bp_add( bp : int ) -> None :
    global BREAKPOINTS
    if not bp in BREAKPOINTS :
        BREAKPOINTS.append( bp )

def bp_rem( bp : int ) -> bool :
    global BREAKPOINTS
    if bp in BREAKPOINTS :
        BREAKPOINTS.remove( bp )
        return True
    return False # it wasn't there

'''
Initialize the module on first load. We get a settings object
and save it.

TODO  Do we do anything with it?
'''

from PyQt5.QtCore import QSettings

def initialize( settings : QSettings ) -> None :
    global SETTINGS
    SETTINGS = settings
    reset_vm( )
    bp_clear( )

'''
Shut down the module, saving anything useful in the settings.

TODO: anything here?
'''

def closeEvent( ) -> None :
    pass

'''
Note passage of 1/60th of second by decrementing the T and S regs.
If the sound was on and goes to 0, turn the sound off.
'''

def tick( ) -> None :
    global REGS
    if REGS[R.T] :
        REGS[R.T] -= 1
    if REGS[R.S] :
        REGS[R.S] -= 1
        if REGS[R.S] == 0 :
            display.sound( False )


'''

        The Emulator Proper Starts Here

'''

'''

Define the error messages that can be detected while decoding and executing
instructions. For simplicity all have the INST and PC values formatted in.

'''

EMSG_BAD_INST = 'Undefined instruction {0:04X} at {1:04X}'
EMSG_BP = 'Breakpoint on {0:04X} at {0:04X}'
EMSG_BAD_CALL = 'Subroutine call but stack is full {0:04X} at {1:04X}'
EMSG_BAD_RET = 'Return but empty call stack {0:04X} at {1:04X}'
EMSG_EXIT = 'Emulator termination {0:04X} at {1:04X}'
EMSG_BAD_ADDRESS = 'Reference to memory beyond 4095 in {0:04X} at {1:04X}'

'''
Factor out formatting of these messages.
'''

def emsg_format( msg: str, INST: int, PC: int ) -> str :
    return msg.format( INST, PC )

'''
            Instruction implementations

Fun Python fact: in a Class definition, you can forward-reference the name
of a class member. For example you could have,
    Class foo():
        self.forward_reference = self.method_name()
This is not a problem even though method_name() has not been defined. (This is
presumably the case because the code will not actually execute until an object
is instantiated, by which time all the class's names are known.)

Sad Python fact: in open code in a module, you cannot. For example to write

    FORWARD = function_not_defined_yet()

produces an error at execution. That's because such a global statement is
executed when it is read.

Well, the following code depends on having dictionaries whose values are
function names, see for example dispatch_first_nybble and others, far (far)
below. In a class definition these dicts could be class variables right at
the top of the class. But in a module we have to write as in Pascal, defining
all the functions before they can be referenced.

So, here are all the functions that implement instructions. For the code that
calls these functions, look further down.

Each of the implementation functions take args of INST, the 16-bit instruction
being executed, and PC, the memory address of the instruction.

When a function detects an error it raises a ValueError exception with an
appropriate error string. This exception is handled in the step() function,
and results in returning the error string to the caller.

When a function finds no error, it returns the updated PC value. In most cases
that is PC+2, the address of the next sequential instruction. For skips it may
be PC+2 or +4. For jumps and calls, it is the target of the jump or call; for
return it is the value popped off the call stack.

See also do_wait_key() for a special case.
'''

'''
00Cx scroll down x lines. This is an SCHIP instruction. However
we leave it to the display module to decide whether it can be
executed, or how.
'''
def do_scroll_down( INST : int, PC : int ) -> int :
    display.scroll_down( INST & 0x000F )
    return PC+2

'''
00E0, clear the display
'''
def do_clear( INST : int, PC : int ) -> int :

    display.clear()
    return PC+2

'''
00EE return from subroutine. Check for empty call stack.
'''
def do_sub_return( INST : int, PC : int ) -> int :
    global CALL_STACK

    if 0 == len( CALL_STACK ) :
        raise ValueError( emsg_format( EMSG_BAD_RET, INST, PC ) )

    return CALL_STACK.pop()

'''
00FB scroll right 4 pixels (2 pixels in CHIP8 mode)
'''
def do_scroll_right( INST : int, PC : int ) -> int :

    display.scroll_right()
    return PC+2

'''
00FC scroll left 4 pixels (2 pixels in CHIP8 mode)
'''
def do_scroll_left( INST: int, PC: int ) -> int :

    display.scroll_left()
    return PC+2

'''
00FD Emulator exit request.
'''
def do_exit( INST: int, PC: int ) -> int :

    raise ValueError( emsg_format( EMSG_EXIT, INST, PC ) )

'''
00FE set CHIP-8 graphics (32x64)
'''
def do_small_screen( INST: int, PC: int ) -> int :

    display.set_mode( False )
    return PC+2

'''
00FF set SCHIP graphics (64x128)
'''
def do_big_screen( INST: int, PC: int ) -> int :

    display.set_mode( True )
    return PC+2

'''
1xxx, JUMP xxx

A jump to xxx == FFF would be an error, as there is not room for a two-byte
instruction. Also, we should not permit a jump to below 0200, which in the
original system would jump into the machine code of the emulator.
'''
def do_jump( INST: int, PC: int ) -> int :

    target = INST & 0x0FFF
    if ( target < 0x0200 ) or ( target == 0x0FFF ) :
        raise ValueError( emsg_format( EMSG_BAD_ADDRESS, INST, PC ) )
    return target

'''
2xxx, CALL xxx
'''
def do_gosub( INST: int, PC: int ) -> int :
    global CALL_STACK

    if len( CALL_STACK ) < MAX_CALL_DEPTH :
        CALL_STACK.append( PC+2 )
        return INST & 0x0FFF

    raise ValueError( emsg_format( EMSG_BAD_CALL, INST, PC ) )

'''
3vxx, SKE v, xx
coding note: yes, this whole thing could be a one-liner.
'''
def do_skip_eq_xx( INST: int, PC: int ) -> int :

    xx = INST & 0x00FF
    v = REGS[ (INST & 0x0F00) >> 8 ]
    return PC + ( 4 if v == xx else 2 )

'''
4vxx, SKNE v, xx
'''
def do_skip_ne_xx( INST: int, PC: int ) -> int :

    xx = INST & 0x00FF
    v = REGS[ (INST & 0x0F00) >> 8 ]
    return PC + ( 4 if v != xx else 2 )

'''
5vw0, SKE v, w
'''
def do_skip_eq( INST: int, PC: int ) -> int :

    v = REGS[ (INST & 0x0F00) >> 8 ]
    w = REGS[ (INST & 0x00F0) >> 4 ]
    return PC + ( 4 if v == w else 2 )

'''
6vxx, LOAD v, xx
'''
def do_load_v( INST: int, PC: int ) -> int :
    global REGS

    REGS[ (INST & 0x0F00) >> 8 ] = INST & 0x00FF
    return PC+2

'''
7vxx, ADD t, xx. Unlike 8ts4, add reg to reg, this add does not set the carry
flag in vF. This is historic; the VIP manual is specific about which
instructions change VF and this isn't one of them. So if you care about
overflow, use 8ts4 instead.
'''
def do_add_v( INST: int, PC: int ) -> int :
    global REGS

    xx = INST & 0x00FF
    t = (INST & 0x0F00) >> 8
    sum = int( xx + REGS[ t ] )
    REGS[ t ] = sum & 0x00FF
    return PC+2

'''
8ts0, LD vt, vs
'''
def do_assign( INST: int, PC: int ) -> int :
    global REGS

    REGS[ (INST & 0x0F00) >> 8 ] = REGS[ (INST & 0x00F0) >> 4 ]
    return PC+2

'''
8ts1, OR vt, vs
'''
def do_or( INST: int, PC: int ) -> int :
    global REGS

    REGS[ (INST & 0x0F00) >> 8 ] |= REGS[ (INST & 0x00F0) >> 4 ]
    return PC+2

'''
8ts2 AND vt, vs
'''
def do_and( INST: int, PC: int ) -> int :
    global REGS

    REGS[ (INST & 0x0F00) >> 8 ] &= REGS[ (INST & 0x00F0) >> 4 ]
    return PC+2

'''
8ts3 XOR vt, vs
Historical note: XOR is not mentioned in Weisbecker's BYTE article
or the VIP manual, but it existed and was quickly found by users who
documented it in the VIPER fanzine.
'''
def do_xor( INST: int, PC: int ) -> int :
    global REGS

    REGS[ (INST & 0x0F00) >> 8 ] ^= REGS[ (INST & 0x00F0) >> 4 ]
    return PC+2

'''
8ts4 ADD vt, vs (carry to F)
'''
def do_add( INST: int, PC: int ) -> int :
    global REGS

    t = (INST & 0x0F00) >> 8
    s = (INST & 0x00F0) >> 4
    sum = int( REGS[ t ] + REGS[ s ] )
    REGS[ R.vF ] = 0 if sum < 256 else 1
    REGS[ t ] = sum & 0x00FF
    return PC+2

'''
8ts5, SUB vt, vs (not-borrow to F) Why did Weisbecker spec that vF is 1 if
there is NO borrow? Must have been something to do with the 1800 chip's
arithmetic. It doesn't matter; the test for borrow would be "SKE vF,x"
and it doesn't matter if x is 0 or 1.
'''
def do_sub( INST: int, PC: int ) -> int :
    global REGS

    t = (INST & 0x0F00) >> 8
    s = (INST & 0x00F0) >> 4
    diff = int( REGS[ t ] - REGS[ s ] )
    if diff < 0 :
        REGS[ R.vF ] = 0
        diff += 256 # -1 goes to 255, etc.
    else :
        REGS[ R.vF ] = 1
    REGS[ t ] = diff
    return PC+2

'''
8t06 SHR vt

The shift-left and -right instructions are not mentioned in the VIP manual
either, but were found by users. However most emulator implementations are
incorrect. The only authoritative reference I have found is Matthew
Mikolay's, developed for the VIP group (groups.yahoo.com/rcacosmac).
'''
def do_shr( INST: int, PC: int ) -> int :
    global REGS

    t = (INST & 0x0F00) >> 8
    s = (INST & 0x00F0) >> 4
    tval = REGS[ s ]
    REGS[ R.vF ] = tval & 0x0001
    REGS[ t ] = tval >> 1

    return PC+2

'''
8ts7 SUBR vt, vs (not borrow to F)

This peculiar instruction subtracts vt from vs with the result to vt. It must
be useful in some graphics algorithm?
'''
def do_subr( INST: int, PC: int ) -> int :
    global REGS

    t = (INST & 0x0F00) >> 8
    s = (INST & 0x00F0) >> 4
    diff = int( REGS[ s ] - REGS[ t ] ) # only difference from do_sub
    if diff < 0 :
        REGS[ R.vF ] = 0
        diff += 256 # -1 goes to 255, etc.
    else :
        REGS[ R.vF ] = 1
    REGS[ t ] = diff
    return PC+2

'''
8t0E, SHL vt
'''
def do_shl( INST: int, PC: int ) -> int :
    global REGS

    t = (INST & 0x0F00) >> 8
    s = (INST & 0x00F0) >> 4
    tval = REGS[ s ]
    REGS[ R.vF ] = 1 if (tval & 0x0080) else 0
    REGS[ t ] = ( tval << 1 ) & 0x00FF

    return PC+2

'''
9vw0, SKNE v, w
'''
def do_skip_ne( INST: int, PC: int ) -> int :
    v = REGS[ (INST & 0x0F00) >> 8 ]
    w = REGS[ (INST & 0x00F0) >> 4 ]
    return PC + ( 2 if v == w else 4 )

'''
Axxx, LOAD I, xxx
'''
def do_load_i( INST: int, PC: int ) -> int :
    global REGS

    REGS[ R.I ] = INST & 0x0FFF
    return PC+2

'''
Bxxx, JUMP xxx + v0

Note the VIP would not notice a jump address beyond the physical memory (2048
or 4096), it would have simply wrapped to an address modulo the memory size
-- which would have necessarily been below 0200, hence an error. Also, an
explicit jump into memory below 0x0200 would always be a bug.
'''
def do_jump_indexed( INST: int, PC: int ) -> int :

    target = REGS[R.v0] + ( INST & 0x0FFF )
    if ( target < 0x0FFE ) and ( target > 0x01FF ) :
        return target # effect the jump

    raise ValueError( emsg_format( EMSG_BAD_ADDRESS, INST, PC ) )

'''
    0xC000 :,   # Cvkk, LOAD v with random byte & kk
'''
import random

def do_load_random( INST: int, PC: int ) -> int :
    global REGS

    target_reg = ( INST & 0x0F00 ) >> 8
    value = random.randint(0,255)
    REGS[ target_reg ] = value & INST # not a mistake, think about it
    return PC+2

'''
Dxxx, draw sprite

We collect the sprite as a list of ints by slicing memory. One error is
remotely possible and we check for it.

We support the SCHIP feature that sprite length of 0 means a 16-bit x 16-bit (32-byte)
sprite. The whole sprite as a list of bytes is passed to
display.draw_sprite() for drawing. It returns True if any white pixel matched
an existing white pixel, erasing it.
'''
def do_draw_sprite( INST: int, PC: int ) -> int :
    global REGS # to update vF
    x_coord = REGS[ ( INST & 0x0F00 ) >> 8 ]
    y_coord = REGS[ ( INST & 0x00F0 ) >> 4 ]

    count = INST & 0x000F
    if count == 0 :
        '''
        Special SCHIP mode: sprite has 16 rows of 16 bits, in 32 consecutive
        bytes.
        '''
        count = 32

    address = REGS[ R.I ]

    if ( address + count ) > 4095 : # unlikely error
        raise ValueError( emsg_format( EMSG_BAD_ADDRESS, INST, PC ) )

    sprite = MEMORY[ address : address+count ]
    hit = display.draw_sprite( x_coord, y_coord, sprite )
    REGS[ R.vF ] = 1 if hit else 0
    return PC+2


'''
Ex9E : skip if key vx is down
ExA1 : skip if key vx is up
Each tests the keypad key whose number (mod 16) is in reg vx.
'''
def decode_Exxx( INST: int, PC: int ) -> int :

    reg = (INST & 0x0F00) >> 8
    key = REGS[ reg ] & 0x0F
    down_key = display.key_test() # a down key or None

    instruction = INST & 0xF0FF
    if instruction == 0xE09E :
        if down_key == key :
            PC += 2

    elif instruction == 0xE0A1 :
        if down_key != key :
            PC += 2

    else:
        raise ValueError( emsg_format( EMSG_BAD_INST, INST, PC ) )

    return PC+2

'''
F007, LD vx, DT
'''
def do_read_timer( INST: int, PC: int ) -> int :
    global REGS

    REGS[ (INST & 0x0F00) >> 8 ] = REGS[ R.T ]
    return PC+2

'''
0xFx0A, wait for a key.

This instruction locks up the virtual machine until a key is pressed. However
we do not want to enter a solid loop testing for a key because that would
prevent Qt events from being processed, which would mean the display window
could never register the key-press! Also, we want to let the user break out
of this instruction by clicking off the Run button in the Memory window.

So in order to get the key repeated, but not monopolize the CPU, we play a
trick: if no key is pressed we return PC, which means this instruction will
be executed again. Only if a key is pressed do we return the normal PC+2.
'''

def do_wait_key( INST: int, PC: int ) -> int :
    global REGS

    key = display.key_test()
    if key < 0 : # no key pressed,
        return PC # ..try again

    REGS[ ( INST & 0x0F00 ) >> 8 ] = key
    return PC+2 # ok to carry on

'''
F015, LD DT, vx
'''
def do_load_timer( INST: int, PC: int ) -> int :
    global REGS

    REGS[ R.T ] = REGS[ (INST & 0x0F00) >> 8 ]
    return PC+2

'''
F018, LD ST, vx
If we are setting the sound timer to a nonzero value we need
also to start the tone going, and if to zero, stop it.
'''
def do_set_tone( INST: int, PC: int ) -> int :
    global REGS

    val = REGS[ (INST & 0x0F00) >> 8 ]
    REGS[ R.S ] = val
    display.sound( val != 0 )

    return PC+2

'''
F01E, ADD I, vx
Note that this could at least in principle set I to >4095. See the
instructions that use I (Bxxx, F055/65) for a comment.
'''
def do_add_to_I( INST: int, PC: int ) -> int :
    global REGS

    val = REGS[ (INST & 0x0F00) >> 8 ]
    REGS[ R.I ] += val
    return PC+2

'''
F029, LD I, vx

Load I with the address of one of the 16 character sprites, the patterns of
the hex characters 0..F. This is the CHIP-8 instruction and uses the 4x5
fonts, located at 0x000..0x004F on reset, see comment in reset_vm().

Note that unlike other emulators which do not check the value of [vx],
here we make sure to only use the low-order nybble in the address.
'''
def do_load_chip8_sprite( INST: int, PC: int ) -> int :
    global REGS

    font_width = 5
    font_base = 0

    character = REGS[ (INST & 0x0F00) >> 8 ] & 0x0F

    REGS[ R.I ] = font_base + ( font_width * character )

    return PC+2

'''
F030, LDH I, vx

Load I with the address of the high-resolution sprite for the character in vx.
'''
def do_load_schip_sprite( INST: int, PC: int ) -> int :
    global REGS

    font_width = 10
    font_base = 0x0050

    character = REGS[ (INST & 0x0F00) >> 8 ] & 0x0F

    REGS[ R.I ] = font_base + ( font_width * character )

    return PC+2

'''
F033, STBCD vx

Convert the byte in register vx to decimal and store the three
bcd characters in memory at I+0, +1, +2. I-reg is unchanged.
'''
def do_store_decimal( INST: int, PC: int ) -> int :
    global MEMORY

    I_reg = REGS[ R.I ]
    if I_reg > 4093 :
        raise ValueError( emsg_format( EMSG_BAD_ADDRESS, INST, PC ) )
    vx = REGS[ (INST & 0x0F00) >> 8 ]
    MEMORY[ I_reg ] = int( vx/100 ) # high digit
    MEMORY[ I_reg + 1 ] = int( vx % 100 / 10 )
    MEMORY[ I_reg + 2 ] = int( vx % 10 )
    MEMORY_CHANGED = True
    return PC+2

'''
F055, STM v0, vx

Store the sequence of registers from v0 through vx (a total of vx+1 bytes)
into memory at the I-reg value. The I-reg is incremented.

Note that in the code of both Craig Thomas's and Brad Miller's emulators this
and the next instruction are implemented incorrectly. Neither increments the value
of the I-reg. This might be blamed on Cowgod's well-known emulator document, which
does not mention incrementing the I-reg. However it is explicit in the original
COSMAC manual and it is correctly documented in Matthew Mikolay's essay.

Based on this, one may assume these instructions are not often used, or at least,
few if any programs actually depend on the I-reg being incremented.

Also neither one checks for invalid address. In the COSMAC VIP, storing v0-v1
at 4095 (for example) would have either resulted in storing v1 at location
0000 (if memory wrapped around) or attempting to store it in a nonexistent
address or in ROM, probably ignored by the hardware. Either is clearly a bug.
In emulated memory it would raise an index error (in Python) or store outside
the allocation (in CPP).

'''
def do_store_regs( INST: int, PC: int ) -> int :
    global REGS, MEMORY

    vx = (INST & 0x0F00) >> 8
    I_reg  = REGS[R.I]
    if I_reg > (4095 - vx) :
        raise ValueError( emsg_format( EMSG_BAD_ADDRESS, INST, PC ) )

    for i in range( vx+1 ) :
        MEMORY[ I_reg ] = REGS[ i ]
        I_reg += 1

    MEMORY_CHANGED = True

    REGS[R.I] = I_reg # "I = I + X + 1" as per COSMAC manual
    return PC+2

'''
F065, LDM v0, vx

Do the inverse of F035, load the registers v0..vx (vx+1 bytes) from memory
at the I-reg value, and increment I. Same comments as above.
'''
def do_load_regs( INST: int, PC: int ) -> int :
    global REGS, MEMORY

    vx = (INST & 0x0F00) >> 8
    I_reg  = REGS[R.I]
    if I_reg > (4095 - vx) :
        raise ValueError( emsg_format( EMSG_BAD_ADDRESS, INST, PC ) )

    for i in range( vx+1 ) :
        REGS[ i ] = MEMORY[ I_reg ]
        I_reg += 1

    REGS[R.I] = I_reg # "I = I + X + 1" as per COSMAC manual
    return PC+2

'''

        End of implementation functions. Start of execution control.
'''

'''
The following dict relates members of the 0xxx group to their implementation
functions.
'''
dispatch_00xx = {
    0x00C0 : do_scroll_down,  # 00Cx scroll down x lines -- SCHIP
    0x00E0 : do_clear,        # 00E0 clear the display
    0x00EE : do_sub_return,   # 00EE return from subroutine
    0x00FB : do_scroll_right, # 00FB scroll right 4 pixels (2 pixels in CHIP8 mode)
    0x00FC : do_scroll_left,  # 00FC scroll left 4 pixels (2 pixels in CHIP8 mode)
    0x00FD : do_exit,         # 00FD exit the emulator
    0x00FE : do_small_screen, # 00FE set CHIP-8 graphics (32x64)
    0x00FF : do_big_screen    # 00FF set SCHIP graphics (64x128)
    }

'''
Decode and dispatch the 0xxx instructions. 00Cx requires special handling
because it contains a variable number x. The others are single unchanging
values.
'''

def decode_0xxx( INST : int, PC : int ) -> int :

    key = INST & 0x00FF

    if 0x00C0 == key & 0x00F0 :
        key = 0x00C0

    try :

        return dispatch_00xx[ key ]( INST, PC )

    except KeyError as KE :

        raise ValueError( emsg_format( EMSG_BAD_INST, INST, PC ) )

'''
The following dict relates the members of the the 8xxx instruction group
to their implementation functions.
'''
dispatch_8xxx = {
    0x8000 : do_assign,     # 8ts0 LD vt, vs
    0x8001 : do_or,         # 8ts1 OR vt, vs
    0x8002 : do_and,        # 8ts2 AND vt, vs
    0x8003 : do_xor,        # 8ts3 XOR vt, vs
    0x8004 : do_add,        # 8ts4 ADD vt, vs (carry to F)
    0x8005 : do_sub,        # 8ts5 SUB vt, vs (not-borrow to F)
    0x8006 : do_shr,        # 8t06 SHR vt
    0x8007 : do_subr,       # 8ts7 SUBR vt, vs (not borrow to F)
    0x800E : do_shl         # 8t0E SHL vt
    }

'''
Decode and execute an 8xxx instruction.
'''
def decode_8xxx( INST:int, PC:int ) -> int :

    key = INST & 0xF00F
    try :

        return dispatch_8xxx[ key ]( INST, PC )

    except KeyError as KE :

        raise ValueError( emsg_format( EMSG_BAD_INST, INST, PC ) )


'''
The following dict relates the members of the F0xx group to their
implementation functions.
'''
dispatch_Fxxx = {
    0xF007 : do_read_timer, # LD vx, DT
    0xF00A : do_wait_key,   # LD vx, KBD
    0xF015 : do_load_timer, # LD DT, vx
    0xF018 : do_set_tone,   # LD ST, vx
    0xF01E : do_add_to_I,   # ADD I, vx
    0xF029 : do_load_chip8_sprite, # LDC I, vx
    0xF030 : do_load_schip_sprite, # LDH I, vx
    0xF033 : do_store_decimal, # STBCD vx
    0xF055 : do_store_regs, # STM v0, vx
    0xF065 : do_load_regs   # LDM v0, vx
    }

'''
Decode and dispatch the Fxxx instructions, which deal with timer,
sound and the I-reg.
'''
def decode_Fxxx( INST:int, PC:int ) -> int :

    key = INST & 0xF0FF
    try :

        return dispatch_Fxxx[ key ]( INST, PC )

    except KeyError as KE :

        raise ValueError( emsg_format( EMSG_BAD_INST, INST, PC ) )
'''

The following dict relates the most significant nybble of an instruction to
one of fifteen functions.

'''

dispatch_first_nybble = {
    0x0000 : decode_0xxx,      # decode several instructions
    0x1000 : do_jump,          # 1xxx, JUMP xxx
    0x2000 : do_gosub,         # 2xxx, CALL xxx
    0x3000 : do_skip_eq_xx,    # 3vxx, SKE v, xx
    0x4000 : do_skip_ne_xx,    # 4vxx, SKNE v, xx
    0x5000 : do_skip_eq,       # 5vw0, SKE v, w
    0x6000 : do_load_v,        # 6vxx, LOAD v, xx
    0x7000 : do_add_v,         # 7vxx, ADD v, xx
    0x8000 : decode_8xxx,      # decode logical instructions
    0x9000 : do_skip_ne,       # 9vw0, SKNE v, w
    0xA000 : do_load_i,        # Axxx, LOAD I, xxx
    0xB000 : do_jump_indexed,  # Bxxx, JUMP xxx + v0
    0xC000 : do_load_random,   # Cvkk, LOAD v with random byte & kk
    0xD000 : do_draw_sprite,   # Dxxx, draw sprite
    0xE000 : decode_Exxx,      # decode keypad tests
    0xF000 : decode_Fxxx       # decode various I-reg ops
    }

'''

        FINALLY!

Execute one emulated machine instruction at the current PC.
   Return None if there is no reason to stop execution.
   Return a message string in case of an error or breakpoint.

This method is called from the Memory module to implement the Run and Stop
buttons.
'''

def step( ) -> str :
    global REGS

    PC = REGS[R.P]
    INST = ( MEMORY[PC] << 8 ) | MEMORY[PC+1]
    error_message = None

    try:

        REGS[R.P] = dispatch_first_nybble[ INST & 0xF000 ]( INST, PC )
        if REGS[R.P] in BREAKPOINTS :
            error_message = emsg_format( EMSG_BP, 0, REGS[R.P] )

    except ValueError as VE :

        # error raised in an implementation function.
        error_message = str( VE )

    except Exception as WUT :

        # programming error in emulator
        error_message = 'Error in IDE: ' + str(WUT)

    return error_message # which is usually None

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
#
# Enter the wonderful world of unit test... which is all ad-hoc-ery with
# minimal commenting. Literate programming waits outside the door.
#

if __name__ == '__main__' :

    from binasm import binasm
    testregs = { r:0 for r in R }
    testregs[R.P] = 0x0200

    # test reset_vm
    reset_vm()
    assert testregs == REGS
    assert 4096 == len(MEMORY)
    assert 0 == sum(MEMORY[512:])

    # test LD v,xx and EXIT
    simprog = binasm( '6321 00FD' )
    reset_vm( simprog )

    assert MEMORY[512:516] == simprog
    s = step()
    assert s is None
    assert REGS[R.v3] == 33
    s = step()
    assert s.startswith(EMSG_EXIT[0:20])
    assert '0202' in s

    # test breakpoint
    reset_vm( simprog )
    bp_add( 0x202 )
    s = step()
    assert s.startswith( 'Breakpoint' )

    # test bad inst
    reset_vm( )
    s = step()
    assert s == emsg_format( EMSG_BAD_INST, 0, 512 )

    # not tested 00Cx scroll
    # not tested 00E0 clear
    # test call, return
    simprog = binasm( '2202 00EE' )
    reset_vm( simprog )
    s = step( )
    assert s is None
    assert REGS[R.P] == 0x0202
    assert CALL_STACK == [ 0x0202 ]
    s = step( )
    assert s is None
    assert REGS[R.P] == 0x0202
    assert 0 ==len( CALL_STACK )
    s = step( )
    assert s == emsg_format( EMSG_BAD_RET, 0x00EE, 0x0202 )
    # not tested 00FB 00FC scroll
    # not tested 00FE 00FF set mode
    # test 1xxx JP
    simprog = binasm( '1204 0000 11FE' )
    reset_vm( simprog )
    s = step( )
    assert s is None
    assert REGS[R.P] == 0x0204
    s = step( )
    assert s == emsg_format( EMSG_BAD_ADDRESS, 0x11FE, 0x0204 )
    # test 3vxx SKE 4vxx SKNE 5vw0 SKE
    # if any fail to skip we hit a 0000 bad inst
    simprog = binasm( '37CC 0000 4733 0000 5780 0000 1200 ' )
    reset_vm( simprog )
    REGS[R.v7] = 0xCC
    REGS[R.v8] = 0xCC
    s = step( )
    assert s is None and REGS[R.P] == 0x204
    s = step( )
    assert s is None and REGS[R.P] == 0x208
    s = step( )
    assert s is None and REGS[R.P] == 0x20C

    # test LD t,s and ADDs
    simprog = binasm( '63FE 8430 7304 8434 ' )
    reset_vm( simprog )
    step( )
    assert s is None and REGS[R.P] == 0x202
    assert REGS[R.v3] == 0xFE
    step( )
    assert s is None and REGS[R.P] == 0x204
    assert REGS[R.v4] == 0xFE
    step( )
    assert s is None and REGS[R.P] == 0x206
    assert REGS[R.v3] == 0x02
    assert REGS[R.vF] == 0x00 # no carry
    step( )
    assert s is None and REGS[R.P] == 0x208
    assert REGS[R.v4] == 0x00
    assert REGS[R.vF] == 0x01 # carry

    # test OR, AND, XOR
    simprog = binasm( '6955 6AAA 89A1 89A2 89A3 ' )
    reset_vm( simprog )
    step( )
    assert s is None and REGS[R.P] == 0x202
    step( )
    assert s is None and REGS[R.P] == 0x204
    step( )
    assert s is None and REGS[R.P] == 0x206
    assert REGS[R.v9] == 0xFF
    step( )
    assert s is None and REGS[R.P] == 0x208
    assert REGS[R.v9] == 0xAA
    step( )
    assert s is None and REGS[R.P] == 0x20A
    assert REGS[R.v9] == 0


