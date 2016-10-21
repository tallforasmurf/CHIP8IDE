
# CHIP8IDE

CHIP8IDE is a programming and execution environment based on the CHIP-8 and
SCHIP-48 virtual machines. CHIP-8 is a virtual machine originally designed
for the COSMAC VIP, an early microcomputer kit. SCHIP is a later enhancement
written for the HP-48 graphing calculator. (More history is given below.)

CHIP8IDE supports entry, editing, assembly, disassembly, execution and
debugging of programs written for the S/CHIP-8 architecture.

## User interface

CHIP8IDE puts up three independent windows, the Display window, the Memory
window, and the Source window; and manages a single menu, the File menu.

### Display window

The Display window contains the emulated screen output of the program, as a
white-on-black array of square pixels. It has 32x64 pixels in CHIP-8 mode, or
64x128 pixels in SCHIP mode. The emulated program can change mode with
machine instructions.

The Display window also presents an emulated 16-key keypad. When an emulated
program is running, it can take input from the keypad. The keys can be
clicked with the mouse or, while the focus is in the Display window, actual
keystrokes are mapped to the displayed key tops.

You can configure which keys operate which virtual keypad keys by
(method TBS) TODO.

### Memory window

The Memory window has a scrolling display of the emulated 4KB of memory. It
also shows the contents of the CHIP-8 machine registers, and the subroutine
call-stack. While the emulator is not running, you can edit the contents of
the displayed memory and the machine registers. It is possible to enter small
programs directly into memory in hexadecimal.

The Memory window offers a Step button that causes the emulator to execute a
single instruction and stop.

The Memory window has a Run button to start execution of the emulator. The
emulator then runs freely until the Run button is clicked again, or an error
occurs, or a breakpoint is reached. While the emulator is running freely, the
display window updates and responds to keypad clicks.

The Memory window offers a spinbox for setting the number of emulated
instructions to execute between 1/60th-second "ticks". This can be set to
regulate the effective speed of the emulated program.

Also in the Memory window is a message area where error and status messages
appear, for example when the emulator encounters an illegal instruction the
error is displayed here.

### Source window

The Source window contains a plain text editor for entering and editing
CHIP-8 assembly language statements. As statements are entered they are
parsed and assembled immediately. The assembled hexadecimal value of each
statement is shown on the same line.

When a statement has incorrect syntax, that line has a pink background and
its assembled value is $0000.

When a statement refers to a symbol that is not yet defined, it has a yellow
background and any memory offset value is set to zero. When the symbol is
defined (or redefined), statements that refer to it are reassembled
automatically.

The source window has a Load button, which causes the current value of the
assembled program to be loaded into the emulator and the emulated program
state to be cleared (all registers zero and the PC at #200).

You can control-click on any statement to toggle it into a breakpoint, or to
remove breakpoint status. While the emulator is executing and execution
reaches a breakpoint line, the emulator stops and the breakpoint line is
highlighted in the Source window.

### File menu

The program has the following commands in its only menu, the File menu.

The Load command queries the user for a file to open. When a file is
selected, the action depends on the type and contents of the file.

TODO: decide on file suffixes - research traditional ones: .c8?

TODO: can handle binary input?

If the file is an assembly source file, it is loaded into the Source window.
If the file is an executable CHIP-8 program it is disassembled and the
disassembly source is loaded into the Source window. In either case, click
Load in the Source window to put the binary program in the emulated memory,
and click Run in the Memory window to execute it.

The Save command queries for a filename to save the current source file.

(There is no Save operation to make a binary file from the Memory state.
There is no advantage to being able to save and reload a binary. It takes
only a click of the Load button and essentially zero time to prepare a source
file for execution.)

## Included Extras

Beside the executable CHIP8IDE program, the distributed bundle includes some
documents and a selection of game programs written for the S/CHIP-8.

### Documents

* *Assembly Cheat-sheet is a summary of the form of the assembly
  language this app supports, including assembler directives and error
  messages.

* *An Easy Programming System* by Joseph Weisbecker is an article that
  appeared in BYTE magazine in 1978. Weisbecker, while employed at RCA,
  designed the CHIP-8 language and interpreter for the COSMAC VIP
  single-board computer, which he also designed. This article describes
  the CHIP-8 design and contains a complete game program for the system.

* *COSMAC VIP Manual* is an abbreviated copy of the original RCA manual
  for the VIP. This copy contains only the programming information for
  the CHIP-8 language and the appendix with source listings for
  more than twenty simple games.

### Games

A large number of CHIP-8 game programs are included in the form of assembly
source. Some are from the COSMAC VIP Manual, and many more from David
Winter's site listed below.

## About the CHIP-8

CHIP-8 is a virtual machine originally designed for the COSMAC VIP, an early
microcomputer kit. The VIP was a single-board computer featuring an RCA 1802
microprocessor, 2KB or 4KB of RAM, a 16-key hexadecimal keypad, and an
interface to a standard television. The VIP was sold by mail-order for $275
in 1977-78.

The CHIP-8 emulator in ROM made it possible for users to write and play
simple games. The CHIP-8 language was at a (slightly) higher level than the
machine language of the 1802 chip; in particular it supported graphics
through sprites, primitive sound output, and input from the 16-key pad. Games
like Pong and Breakout could be coded in the 4K memory and played enjoyably.

Later, the SCHIP-48 virtual machine was defined for the HP48 graphing calculator.
It introduced the higher-resolution (64x128) display and a few other changes.
For more on the origin and history of CHIP-8 see the following:

* [Wikipedia article](https://en.wikipedia.org/wiki/CHIP-8) with overview and links.

* Original [COSMAC VIP manual](http://www.mirrorservice.org/sites/www.bitsavers.org/pdf/rca/cosmac/)
  documents the entire single-board computer in detail, including CHIP-8 programming.
  (Another [online copy](https://www.manualslib.com/manual/602113/Rca-Cdp18s711.html) is incomplete,
  lacking most of the pages with CHIP-8 game listings.

* [COSMAC VIP page](http://www.oldcomputers.net/rca-cosmac-vip.html) with
  pictures clearly showing the 16-key keypad.

* [BYTE magazine issue](https://ia802700.us.archive.org/7/items/byte-magazine-1978-12/1978_12_BYTE_03-12_Life.pdf)
  (large PDF) for December 1978 with article by Joseph Weisbecker, author of CHIP-8, describing it.
  The text of this article is included with the distribution.

* [Mastering CHIP-8](http://mattmik.com/files/chip8/mastering/chip8.html), an essay by Matthew Mikolay,
  has a good technical description of the CHIP-8 but omits the SCHIP features.

* [Matthew Mikolay's Retrocomputing page](http://retro.mattmik.com/) has documents,
  some program sources, and PDF copies of  all issues of the fanzine VIPER,
  in which can be found many CHIP-8 game listings.
  [Viper issue 1](http://www.mattmik.com/files/viper/Volume1Issue01.pdf) has a lengthy review
  of the CHIP-8 instructions with tutorial.

* [CowGod's CHIP-8 page](http://devernay.free.fr/hacks/chip8/C8TECH10.HTM) is probably the most frequently
  cited internet reference, and covers both CHIP-8 and SCHIP features
  (but is incorrect on the shift instructions).

## Program Design

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

The module display.py manages the emulated screen and keypad and sound. It
exports functions to the emulator for drawing, key status, and sound.

The module source.py manages the assembly source editor. It also contains a
disassembler that is used to load CHIP-8 binaries into source form. It
implements the File>Load and File>Save operations. It calls on the emulator
to update the list of breakpoint addresses.

The memory, display and source modules make extensive use of PyQt classes and
create PyQt windows and other objects. However, these modules do not offer
their APIs through the class mechanism. For many programmers it would be
almost a reflex to have each module define a class with methods to represent
its capabilities. But this is quite unnecessary (and such "singleton
factories" are accounted as bad O-O design).

In Python, an imported module is a private namespace. Each module uses the
\_\_all\_\_ global variable to define the public names it exports to other
modules. One module gets a service from another by importing it and calling
an exported function. For example, the chip8 module gains access to the
display with code such as,

    import display
    screen_mode = display.get_mode()

The specific list of exported names is documented in each module.

### Type checking

All modules use Python type annotation to document function arguments and
results. TODO: is this being automatically checked?

### Unit tests

Each module has a "if name is main" section that executes basic sanity tests
against the module code. I did not use pytest or nose or any other unit test
framework. The unit tests are just hacked in.

## Sources

In creating CHIP8IDE I have taken explanations, ideas, and some code from
following:

Hans Christian Egeberg wrote CHIPPER, a CHIP-8/SCHIP assembler with output to
a binary file for execution in the HP48 calculator in C, which is still
available from the [HP Calculator
archives](http://www.hpcalc.org/details/6735). The source of CHIPPER
is completely uncommented, but the CHIPPER.DOC file included with it has a
good review of the instructions.

David Winter created a CHIP-8 emulator for MS-DOS. His [CHIP-8
page](http://www.pong-story.com/chip8/) has the source of Egeberg's CHIPPER,
and the source and executable of a number of CHIP-8 and SCHIP games. Although the
source of his own emulator CHIP8.EXE is not included, his CHIP8.DOC file also documents
the instruction set. I have used the games from this page as test vehicles
and have included a number of them in the distribution of CHIP8IDE.

Craig Thomas's [Chip8Python](https://github.com/craigthomas/Chip8Python) is
an elegantly coded CHIP-8 emulator. (But it does SHR/SHL incorrectly.)

"Mudlord" (Brad Miller) wrote a CHIP-8/SCHIP emulator in C++ (https://github.com/mudlord/maxe)
which I have consulted. (But it too has the SHR/SHL instructions wrong.)

Jeffrey Bian wrote [MOCHI-8](http://mochi8.weebly.com/), a CHIP-8 assembler,
disassembler, and emulator, all in Java. The assembler is notably advanced
over CHIPPER, supporting forward references to labels and complex
expressions. I have followed his assembly language syntax, and I referred to
his code and documentation in creating the assembler and disassembler in this
project. (But his emulator also has the SHL/SHR instructions wrong.)
