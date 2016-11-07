# CHIP-8 Assembler Reference

The assembler is case-insensitive. Lowercase character input is treated as uppercase.
In this sheet, **bold** means a value to be
entered exactly as shown, while *italic* means a value to be chosen by you.

## Input rules

An assembler source file consists of lines of ASCII characters only.
When you use File>Open to open a file, Chip8IDE examines the file.
If it consists only of ASCII characters, it assumes it is a source file
and loads it into the editor window.

If you open a file that contains non-ASCII characters, Chip8IDE assumes
you have opened a CHIP-8 or SCHIP *binary* executable.
It automatically disassembles the binary into source statements and
loads these lines into the editor window.

Note if an assembler source file contains accented characters and symbols
that are not in the ASCII set, it will be treated as a binary executable
when it is opened, with hilarious results.

### Statements

Each statement consists of these parts, all of which are optional:

* A label, which is an alphabetic character followed by zero or more alphanumeric characters,
  followed by a colon.
  An underscore may be used as an alphabetic.
  Examples: `Q:`, `DO_DRAW_2:`.

* An opcode, either an instruction name such as `JP` or `LD`,
  or a directive such as `EQU`.

* One or more expressions (depending on the opcode)
  separated by commas. Examples: `V2, V7` or `BUFLEN % #10`.

* A semicolon and a comment, for example `; increment X coord`.

Examples:

    ; just the comment
    EXIT: ; label, comment, no opcode or operands
    SUB_START: LD v3, #FF ; all four parts

### Reserved Names

The following names are reserved and may not be used as labels.

* All opcodes and directives listed below are reserved.

* Data register names, which are:
**v0**, **v1**, ... **v9**, **vA**, **vB**, **vC**, **vD**, **vE** and **vF**.

* The I register is named **I**.

* The timer countdown register is named **DT**.

* The sound countdown register is named **ST**.

* In one instruction, the keyboard is referred to as **K**.

These names should not be used as labels.
For example, `CALL SUB` would be an error because it is
seen as two opcodes (`CALL`, `SUB`) in sequence, not a call to
a label `SUB`.
Similarly, `ST EQU 5` would be seen as a special register,
not a variable `ST` being given the value 5.


### Strings

String data is ASCII characters enclosed in single quotation marks, `'LIKE THIS'`
Use a pair of quotation marks to include a single quotation mark in the string:
`'THAT''S HOW'`. (Strings are used only in the **DA** directive.)
Lowercase letters are forced to uppercase.

### Numeric Values

Numeric values are written as:

* Decimal, `27`

* Hexadecimal when preceded by a hashmark, `#1B`.

* Octal when preceded by an at-sign, `@177`.

* Binary when preceded by a dollarsign, `$00011011`.
When writing binary, you may use a decimal point in place of a zero,
which makes it easier to define sprite values: `$...11.11`.

* A label represents the value of its address, or the value assigned
by the `EQU` directive.

### Expressions

Numeric expressions are allowed using these operators, listed from
highest priority to lowest:

* Parentheses **(** and **)**
* **+** *value* unary plus
* **-** *value* unary minus
* **~** *value* bitwise NOT
* *value* **!** *exp* power-of
* *value* **<** *count* shift *value* left *count* bits
* *value* **>** *count* shift *value* right *count* bits
* *value* ***** *value* multiply
* *value* **/** *value* divide
* *value* **+** *value* add
* *value* **-** *value* subtract
* *value* **&** *value* bitwise AND
* *value* **|** *value* bitwise OR
* *value* **^** *value* bitwise XOR
* *value* **%** *value* modulus (remainder)

## Directives

Directives control the assembly process. The following directives are allowed:

* **DA** *string* The ASCII bytes representing the characters are assembled.

* **DB** *expression* \[**,** *expression*...\] One or more bytes are assembled.

* **DW** *expression* \[**,** *expression*...\] One or more 16-bit words
are assembled (convenient for making SCHIP 16x16 sprites).

* **DS** *expression* Reserve *expression* bytes of space.

* *name* **EQU** *expression* Give the value of *expression* to *name*
so it can be used in other expressions.
You may use **=** in place of **EQU**.

* **ORG** *expression* Set the assembly location to *expression*,
possibly skipping over undefined space or possibly returning to
assemble over bytes assembled previously.

Space reserved by **DS** and space skipped over by **ORG** will be
probably be filled with zeros when the program is loaded (but it
would be bad practice to assume that).

## Instruction Opcodes

In the following descriptions, the hexadecimal form of each instruction
is shown in parentheses. For example the hexadecimal form of `ADD I, Vs`
is `#Fs1E`, where *s* is the number of the specified register.

### Opcodes that change the flow of execution

* **EXIT**

  Stop the emulator. (00FD)

* **JP** *address*

  Jump to specified address. (1aaa)

* **JP v0**, *address*

  Jump to specified address plus contents of **v0** (indexed jump). (Baaa)

* **CALL** *address*

  Push PC on the call stack; jump to specified address. The call stack is
  limited to 12 levels. A thirteenth call forces an error stop. (2aaa)

* **RET**

  Pop top address from call stack into PC: thus, return from subroutine.
  If the call stack is empty, force an error stop. (00EE)

* **SE** **V***s*, *byte*

  Skip the following instruction if the contents of **V***s* equal *byte*. (3sbb)

* **SNE** **V***s*, *byte*

  Skip the following instruction if the contents of **V***s* do not equal *byte*. (4sbb)

* **SE** **V***x*, **V***y*

  Skip the following instruction if the contents of **V***x* equal those of **V***x*. (5xy0)

* **SNE** **V***x*, **V***y*

  Skip the following instruction if the contents of **V***x* do not equal those of **V***x*. (9xy0)

* **SKP** **V***s*

  Skip the following instruction if the key (0-16) specified by **V***s* is down (being pressed). (Es9E)

* **SKNP** **V***s*

  Skip the following instruction if the key (0-16) specified by **V***s* is not pressed. (EsA1)

### Opcodes related to the data registers

* **LD** **V***t*, *byte*

  Put the value of *byte* in register **V***t*. (6tbb)

* **LD** **V***t*, **V***s*

  Put the contents of **V***s* into **V***t*. (8ts0)

* **ADD** **V***t*, *byte*

  Add the value of *byte* to the contents of **V***t*. Overflow is not recorded. (7tbb)

* **ADD** **V***t*, **V***s*

  Add the contents of **V***s* into **V***t*. If the sum overflows eight bits, register
  **VF** is set to 01, else it is set to 00. (8ts4)

* **RND** **V***t*, *byte*

  Generate a random number in 0..255, logically AND it with *byte*,
  and put the result in **V***t*. For example to get a 4-bit
  random number, specify *byte* as 15 or 0xf. (Ctbb)

* **LD** **V***t*, **K**

  Wait for a key to be pressed and put that key (0..16) in **V***t*.
  Note that this ties up the emulator until a key is entered on the display
  or the Run/Stop button is toggled. (Ft0A)

* **OR** **V***t*, **V***s*

  OR the contents of **V***s* and **V***t* and put the result in **V***t*. (8ts1)

* **AND** **V***t*, **V***s*

  AND the contents of **V***s* and **V***t* and put the result in **V***t*. (8ts2)

* **XOR** **V***t*, **V***s*

  XOR the contents of **V***s* and **V***t* and put the result in **V***t*. (8ts3)

* **SUB** **V***t*, **V***s*

  Subtract the contents of **V***s* from **V***t* and put the result in **V***t*.
  If **V***s* <= **V***t*, **VF** is set to 1. If **V***s* > **V***t* there is underflow
  and **VF** is set to 0. (8ts5)

* **SUBN** **V***t*, **V***s*

  Subtract the contents of **V***t* from **V***s* and put the result in **V***t*.
  If **V***t* <= **V***s*, **VF** is set to 1. If **V***t* > **V***s* there is underflow
  and **VF** is set to 0. (8ts5)

* **SHR** **V***t*, **V***s*

  Shift the contents of **V***s* right 1.
  The result is stored in **V***t* (*see note below*).
  The shifted-out bit, 0 or 1, is set as the
  value of **VF**.
  To gain the effect of shifting the contents of a register within that same register,
  specify the same register twice, for example `SHR v5, v5 ; shift v5 right`. (8ts6)

* **SHL** **V***t*, **V***s*

  Shift the contents of **V***s* left 1. The shifted-out bit, 0 or 1, is set as the
  value of **VF**. The result is stored in **V***t* (*see note below*). (8xyE)
  To gain the effect of shifting the contents of a register within that same register,
  specify the same register twice, for example `SHL v3, v3 ; shift v3 left`. (8ts6)

### Opcodes related to the Timer and Sound registers

* **LD** **V***t*, **DT**

  Store the current contents of the **DT** register in **V***t*. (Ft07)

* **LD** **DT**, **V***s*

  Store the contents of **V***s* in the timer register. (Fs15)

* **LD** **ST**, **V***s*

  Store the contents of **V***s* in the sound timer register.
  (There is no instruction for loading the contents from **ST**.) (Fs18)

### Opcodes that change or use the I register

* **LD** **I**, *addr*

  Put the value of *addr* in **I**. (Aaaa)

* **ADD** **I**, **V***s*

  Add the contents of **V***s* to **I**. Note that this can potentially set
  **I** to an address outside memory, that is, >4095). (Fs1E)

* **LDC** **I**, **V***s*

  Load **I** with the address of a CHIP-8 (5x4 pixel) character sprite
  for the number (`0..F`) in the low four bits of **V***s*. (Fs29)

* **LDH** **I**, **V***s*

  Load **I** with the address of the SCHIP (10x8 pixel) character sprite
  for the number in the low four bits of **V***s*. (Fs30)

* **STD** **V***s*

  Store three bytes for the decimal digits of the contents of **V***s* into
  memory at the address in **I**. The **I** contents is incremented by three.
  For example if **V5** contains 0x76 and **I** contains 0x0500,
  the instruction `STD v5` places the bytes #01, #02, #06 into
  memory starting at 0x0500, and **I** will contain #0503. (Fs33)

* **LDM** **V***t*

  Load the data registers from **V0** through **V***t* from memory beginning
  at the address in **I**. The **I** value is incremented for each register
  loaded. This instruction can be used to load the single register **V0**
  from memory addressed by **I**: `LDM V0`.
  
  Another typical use for load-multiple would be to load the three digit
  values stored by **STD** into registers **V0**, **V1** and **V2**, as `LDM V2`. (Ft65)

* **STM** **V***s*

  Store the data registers from **V0** through **V***s* into memory beginning
  at the address in **I**. The **I** value is incremented for each register
  stored. (Fs55)

### Opcodes that affect the display

* **CLS**

  Clear the display to all-black pixels. (00E0)

* **LOW**

  Set the display to CHIP-8 mode, with 32 rows of 64 pixels. The display is cleared. (00FE)

* **HIGH**

  Set the display to SCHIP mode, with 64 rows of 128 pixels. The display is cleared. (00FF)

* **DRAW** **V***x*, **V***y*, *len*

  Draw the sprite currently addressed by **I** on the screen. The X-coordinate
  is taken from **V***x*, the Y-coordinate from **V***y*. The value of *len* specifies
  how many bytes are in the sprite, from 1 to 15.
  If the sprite extends past the right side or bottom row of the display, some pixels
  "wrap" to the left side or top edge. (Dxyn)

  If *len* is 0, **I** must address an SCHIP 16x16 sprite, comprising 32 bytes in all.

* **SCD** *rows*

  Scroll the display down by *rows* (from 0 to 15).
  Note there is no scroll up instruction. (00Cn)

* **SCR**

  Scroll the display right by four pixels. (00FB)

* **SCL**

  Scroll the display left by four pixels. (00FC)

(*Note on SHL and SHR instructions*: These instructions,
along with the XOR and SUBN opcodes, were not documented in the
original COSMAC VIP manual and were later discovered by users who
disassembled the CHIP-8 interpreter code. Unfortunately information
on how SHL and SHR were originally implemented was
reported incorrectly. As a result, most extant emulators do these
instructions incorrectly: they shift **V***s* and put the result in **V***s*, ignoring
**V***t*. This has probably not been noticed because almost all uses of
the instructions name the same register for *vs* and *vt*.
See the README for this program for a link to more information.)
