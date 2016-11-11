
# CHIP8IDE

CHIP8IDE is a programming and execution environment based on the CHIP-8 and
SCHIP-48 virtual machines. CHIP-8 is a virtual machine that was originally
designed for the COSMAC VIP, an early microcomputer kit, in 1977-78.
(More fascinating history is given below.)

CHIP8IDE allows entry, editing, assembly, disassembly, execution and
debugging of programs written for the S/CHIP-8 architecture.

**for current status and to-do list scroll to end**

## User interface

CHIP8IDE puts up three independent windows, the Display window, the Memory
window, and the Source window; and manages a single menu, the File menu.

### Display window

The Display window contains the emulated screen output of the program as a
white-on-black array of square pixels. It has 32x64 pixels in CHIP-8 mode, or
64x128 pixels in SCHIP mode (selected by the emulated program code).

The Display window also presents an emulated 16-key keypad. When an emulated
program is running, it can take input from the keypad. The keys can be
clicked with the mouse or, while the focus is in the Display window,
designated keystrokes are mapped to the displayed key tops.
The user can configure which keys correspond to the virtual keypad keys.

### Memory window

The Memory window has a scrolling display of the emulated 4KB of memory. It
also shows the contents of the CHIP-8 machine registers and its subroutine
call-stack. While the emulator is not running, you can edit the contents of
the displayed memory and the machine registers. It is possible to enter small
programs directly into memory in hexadecimal.

The Memory window offers a Step button that causes the emulator to execute a
single instruction and stop.

The Memory window has a Run button to start free execution of the emulated
program.
The emulator then runs until the Run button is clicked again, or an error
occurs, or a breakpoint is reached. While the emulator is running, the
display window shows the program's output and responds to keypad clicks.

The Memory window offers a spinbox for setting the number of emulated
instructions to execute between 1/60th-second "ticks". This can be set to
regulate the effective speed of the emulated program.

Also in the Memory window is a message area for status messages.
When the emulator has been running and stops, the reason for the stop
is displayed, for example an illegal instruction or a bad memory reference.

### Source window

The Source window contains a plain text editor for entering and editing
CHIP-8 assembly language statements. As statements are entered they are
parsed and lexical errors are diagnosed immediately.

Not all errors can be detected while the program is being edited.
The Source window offers a CHECK button which performs an assembly.
This identifies errors in expressions, undefined labels, and other
mistakes that are not evident to lexical parsing.

When a statement is in error, it is shown with a pink background.
When the edit cursor is on an erroneous statement, the cause of the error
is displayed in a status line below the edit window.
The user can jump quickly from error line to error line by keying control-E.

The Source window offers a LOAD button which causes the program to be
assembled and, if the source is error-free,
its binary value is loaded into the
emulator memory and the emulated program
state is cleared (all registers zero and the PC at #200).
The user can then start execution with the RUN button in the Memory window
and interact with the program in the Display window.

The user can key control-B to toggle any executable source statement into
a breakpoint or to remove its breakpoint status.
Breakpoint lines are shown with a light blue background.
When execution reaches a breakpoint line, the emulator stops.

Whenever the emulator stops execution for any reason, the edit cursor
moves to the source line matching the current PC.

### File menu

The program has the following commands in its only menu, the File menu.

The New command clears the editor and resets the virtual machine.

The Open command queries the user for a file to open. When a file is
selected, the action depends on the type and contents of the file.

CHIP8IDE tests the content of the selected file.
If it is an ASCII file, it is assumed to be an assembly source file and
it is loaded into the Source editor.

When the file is not ASCII (as determined by the Python `bytes.decode('ASCII')`
method), the file is assumed to be an executable CHIP-8 program in binary form.
The file is disassembled and the disassembly source is loaded into the Source
window.

In either case, the user can immediately click LOAD in the Source window
to assemble the program into the emulated memory,
then click RUN in the Memory window to execute it.

The Save command saves the current source file.
The Save As command queries for a filename to save the current source file.
There is no Save operation to make a binary file from the Memory state.
Because both disassembly and assembly are virtually instantaneous,
there is no time advantage to being able to save and reload a binary.
Except for having to click LOAD then RUN,
it takes basically no time to load and run a source program.

## Included Extras

Beside the executable CHIP8IDE program, the distributed bundle includes some
documents and a selection of game programs written for the S/CHIP-8.

### Documents

* *Assembly Reference* is a summary of the form of the assembly
  language this app supports, including assembler directives and error
  messages.

* *An Easy Programming System* by Joseph Weisbecker is an article that
  appeared in BYTE magazine in 1978. Weisbecker, while employed at RCA,
  designed the CHIP-8 language and emulator for the COSMAC VIP
  single-board computer (which he also designed). This article describes
  the CHIP-8 design and contains a complete game program for the system.

* *COSMAC VIP Manual* is an abbreviated copy of the original RCA manual
  for the VIP, containing the programming information for
  the CHIP-8 language and the appendix with source listings for
  more than twenty simple games.

### Games

A large number of CHIP-8 game programs are included, some as executable
binaries and some as commented assembler source.
Some are from the COSMAC VIP Manual; others collected from
various spots around the internet.


## About the CHIP-8

CHIP-8 is a virtual machine originally designed for the COSMAC VIP, an early
microcomputer kit. The VIP was a single-board computer featuring an RCA 1802
microprocessor, 2KB or 4KB of RAM, a 16-key hexadecimal keypad, and an
interface to a standard television. The VIP was sold by mail-order for $275
in 1977-78.

Joseph Weisbecker, who designed the VIP hardware, also designed
the CHIP-8 emulator in order to make it possible for users to write and play
simple games without having to learn the machine language of the 1802 microprocessor.
The CHIP-8 language was at a higher level than the
machine language of the 1802 chip; in particular it supported graphics
through sprites, primitive sound output, and input from the 16-key pad.
Weisbecker coded the entire emulator in 512 bytes of machine code.
(This is why all CHIP-8 programs load at 0x0200: the emulator itself 
occupied bytes 0000-01FF.)

Even though there was no assembler -- so the user had to enter code
directly into memory in hexadecimal -- games
like Pong and Breakout could be coded and played enjoyably.
After a program had been entered and debugged, the user could save
memory to an audio cassette for reloading later.
Programs were shared on audio cassette in the hobbyist community,
and via the user magazine, *VIPER*.

Later, the SCHIP-48 virtual machine was defined to provide an easy way
to write games for the HP48 graphing calculator.
It introduced the higher-resolution (64x128) display and a few other enhancements,
but was basically the same as the CHIP-8, and CHIP-8 programs could run
unchanged on the HP-48.

For more on the origin and history of CHIP-8 see the following:

* [Wikipedia article](https://en.wikipedia.org/wiki/CHIP-8) with overview and links.

* The [COSMAC VIP page](http://www.oldcomputers.net/rca-cosmac-vip.html) at OldComputers.net
  has good pictures of the original machine.

* Online copy of the original [COSMAC VIP manual](http://www.mirrorservice.org/sites/www.bitsavers.org/pdf/rca/cosmac/)
  documents the entire single-board computer in detail, including its hardware
  and ROM. The VIP manual distributed with CHIP8IDE was extracted from this source.
  (Another [online copy](https://www.manualslib.com/manual/602113/Rca-Cdp18s711.html) is incomplete,
  lacking most of the pages with CHIP-8 game listings.)

* [BYTE magazine for December 1978](https://ia802700.us.archive.org/7/items/byte-magazine-1978-12/1978_12_BYTE_03-12_Life.pdf)
  (large PDF) contains the article by Joseph Weisbecker describing CHIP-8.
  A copy of this article is distributed with CHIP8IDE.

* [Mastering CHIP-8](http://mattmik.com/files/chip8/mastering/chip8.html), an essay by Matthew Mikolay,
  has a good technical description of the CHIP-8 but omits the SCHIP features.

* [Matthew Mikolay's Retrocomputing page](http://retro.mattmik.com/) has documents,
  some program sources, and PDF copies of  all issues of the fanzine *VIPER*,
  in which can be found many CHIP-8 game listings.
  [*VIPER* issue 1](http://www.mattmik.com/files/viper/Volume1Issue01.pdf) has a lengthy review
  of the CHIP-8 instructions with a tutorial.

* [CowGod's CHIP-8 page](http://devernay.free.fr/hacks/chip8/C8TECH10.HTM) is probably the most frequently
  cited internet reference, and covers both CHIP-8 and SCHIP features
  (but is incorrect on the shift instructions).

### Undocumented Instructions

There are three original sources of documentation for CHIP-8:
the VIP manual, the BYTE article, and issue 1 of *VIPER*.
All omit to mention three instructions which were supported by Weisenbecker's
emulator code: shift-left, shift-right, and exclusive-or of machine registers.
It is impossible to know if that omission was intentional or a mistake.
Perhaps the instructions were added in a last-minute update before the VIP shipped.

At any rate, they were soon discovered by fans who reverse-engineered the 512-byte machine
language emulator program out of curiosity.
The first description of the added instructions appeared in
[*VIPER* issue 2](http://www.mattmik.com/files/viper/Volume1Issue02.pdf) in a letter to the
editor from Peter K. Morrison that describes the operation of the emulator.
(The same issue has another analysis of the emulator code, with flowcharts!)

Morrison's letter correctly describes the operation of the SHR and SHL instructions:
the value from the source register, V*s*, is shifted and the result is placed in the
target register V*t* (`Vt = Vs<<1` and `Vt = Vs>>1`).

Somehow this became lost over time and an incorrect interpretation has propogated online
which assumes that the value was shifted in-place (`Vt = Vt<<1` etc).
This may have been because most programs that used the instructions *intended* for the
shift to happen in-place, so they coded the same register number for V*t* and V*s*.
At least two of the emulators I've looked at have this incorrect implementation.
And CowGod's influential CHIP-8 Technical Reference also has it wrong.

The correct interpretation of the shift instructions was clarified in a recent exchange
at the [Yahoo VIP Group](https://groups.yahoo.com/neo/groups/rcacosmac/conversations/messages/328).


## Sources

There are many CHIP-8 emulators to be found around the internet.
It is a favorite project for people studying computer science.
I have seen several of these, but in creating CHIP8IDE
I have taken explanations, ideas, and some code from following:

Hans Christian Egeberg wrote CHIPPER, a CHIP-8/SCHIP assembler with output to
a binary file for execution in the HP48 calculator.
It is still available from the [HP Calculator
archives](http://www.hpcalc.org/details/6735). The C source of CHIPPER
is completely uncommented, but the CHIPPER.DOC file included with it has a
good review of the instructions.

David Winter created a CHIP-8 emulator for MS-DOS. His [CHIP-8
page](http://www.pong-story.com/chip8/) has the source of Egeberg's CHIPPER,
and the source and/or executable of a number of CHIP-8 and SCHIP games.
Although the
source of his own emulator CHIP8.EXE is not included, his CHIP8.DOC file also documents
the instruction set. I have used the games from this page as test vehicles
and have included a number of them in the distribution of CHIP8IDE.

Craig Thomas's [Chip8Python](https://github.com/craigthomas/Chip8Python) is
an elegantly coded CHIP-8 emulator (but it does SHR/SHL incorrectly).
I took Python coding ideas from it.

"Mudlord" (Brad Miller) wrote a
[CHIP-8/SCHIP emulator in C++](https://github.com/mudlord/maxe)
which I have consulted. (But it too has the SHR/SHL instructions wrong.)

Jeffrey Bian wrote [MOCHI-8](http://mochi8.weebly.com/), a CHIP-8 assembler,
disassembler, and emulator, all in Java. The assembler is notably advanced
over CHIPPER, supporting forward references to labels and complex
expressions. I have followed his assembly language syntax, and I referred to
his code and documentation in creating the assembler and disassembler in this
project. (But his emulator also has the SHL/SHR instructions wrong.)

Github user "mir3z" has a [JavaScript CHIP-8 emulator](https://github.com/mir3z/chip8-emu)
which I did not actually read.
However, the [rom folder](https://github.com/mir3z/chip8-emu/tree/master/roms) at that site is stuffed with many
S/CHIP-8 executables.

## CHIP8IDE Design

CHIP8IDE is written in Python for version 3.5. It uses Qt 5.7 and PyQt 5.7
for user interface code. The code is written in "literate" style, with code interspersed
among the text of a narrative.

The program is designed around Model/View principles. The module chip8.py is
the "model". It creates and manages the emulated environment (memory and
registers) and executes emulated instructions. Other modules provide
"view/controller" access to this model.

The module chip8ide.py is the top level module which sets up for execution
and starts the PyQt interactive event loop. It initializes the Qt settings (used to
save and restore window geometry and other data), sets up logging, and calls each
other module to initialize itself.

The module memory.py displays the emulated machine state and gives the user
control of the execution of the emulator.
It uses a separate Qt thread to implement the free-running RUN state,
so the emulator can run at speed while the user still interacts with 
Qt widgets.

The module display.py manages the emulated screen and keypad and sound. It
exports functions to the emulator for drawing, key status, and sound.

The module source.py manages the assembly source editor.
It implements the New, Open, Save and Save-As operations.
It interacts with the emulator to manage the list of breakpoint addresses
and to be notified when emulation stops, to center the PC statement.

The source.py code calls on assembler1.py to perform syntax checking
of the statements as they are entered. This code tokenizes each statement,
detects errors, and stores value expressions in the form of Python code objects.

When the CHECK or LOAD button is clicked, source.py calls on assembler2.py
to perform the actual assembly. It uses the tokens and expression code left
by assembler1.py to complete the assembly, in the process detecting various
errors.

The common API shared by source.py, assembler1.py and assembler2.py is the
Statement class, defined in statement.py.
A Statement object represents the tokenized statement and
its status. One Statement object is stored as the userData value of each
editor QTextBlock.

To implement loading a non-ASCII file, source.py calls disassembler.py.
This module performs the disassembly and returns a single string which can
be loaded as the plain text of the editor widget. The disassembler cannot
really fail because any byte it does not recognize as an S/CHIP-8 instruction,
it represents as a `DB #xx` statement.

In Python, an imported module is a private namespace. Each module uses the
`__all__` global variable to define the public names it exports to other
modules. One module gets a service from another by importing it and calling
an exported function. For example, the chip8 module gains access to the
display with code such as,

    import display
    screen_mode = display.get_mode()

The specific list of exported names is documented in each module.

### Type checking

All modules use Python type annotation to document function arguments and
results. It might even be automatically checked...

### Unit tests

Some modules have an "if name is main" section that executes basic sanity tests
against the module code. I did not use pytest or nose or any other unit test
framework. The unit tests are just hacked in. So sue me.

## >>>CURRENT STATUS<<<

* Emulator module substantially complete.
* Memory module substantially complete (see below)
* Source module mostly complete (see below)
* Lexical scan and error display complete
* Assembler substantially complete
* Disassembler complete
* Display shows the emulated screen

TODO: 

All modules:

* add logging
* complete type annotations and run checker

Display:

*   Implement sound
* Add "latch" mode -- control-click? -- to buttons so they will stay
  selected until they are read -- to work with step mode
*   <strike>Code and test keypad</strike>
*   <strike>Design and test keypad/keyboard assignments</strike>
*   <strike>Implement remaining display instructions (scroll, etc)</strike>

Source:

* Figure out what gives with cursor line on insert newline
* Add breakpoint toggling and display (^b)
* Add clear-all-BP button
* Clear all BP on Open, New
* <strike>Add ^E jump to next error</strike>
* <strike>Add Find/Replace dialog, ^f ^g/^G ^t ^= </strike>
* <strike>Jump cursor to PC statement on stop (registry)</strike>
* <strike>On open-binary set name Untitled, clear path</strike>
* <strike>treat tab as 4spaces not 8?</strike>
* <strike>Display assembled value, when known, in status line</strike>

Memory:

* Can't edit register table?
* <strike>Add registry for "stopped" callback</strike>
* <strike>Don't update the memory table unless it has changed</strike>
* <strike>scroll display to 0200 on reset</strike>
* <strike>Highlight current inst. whenever stopped</strike>

Assembler:

* <strike>Add assembled PC to Statement object</strike>
* <strike>Add assembled value to Statement object</strike>

Emulator:
* <strike>Export a flag set by the STD and STM instructions</strike>
* <strike>update both tables on any stop</strike>
* <strike>execution not cleared on LOAD button?</strike>
