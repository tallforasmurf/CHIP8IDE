; This is a simple program to test the chip8 tone
; generator:
; * wait for two hex digits on the keypad.
;   - display the digits as entered.
; * convert the 2 keys to a binary value
; * load that value into the ST and DT regs
; * wait for the DT reg to count down to 0
; * repeat
;
; registers:
;   VD first digit
;   VC second digit
;   VB binary value
;   V2 key input to subroutine
;   V0 x-coord
;   V1 y-coord


TOP:
	CLS ; clear the screen
; get the first digit to VD and show it
	LD	VD, K
	LD	I, FIRST_XY
	LD	V2, VD
	CALL	SHOW_DIGIT	
; get the second one to VC and show it
	LD	VC, K
	LD	I, SECND_XY
	LD	V2, VC
	CALL	SHOW_DIGIT
; convert 2 digits to binary
	SHL	VB, VD ; shift VD contents, put in VB
	SHL	VB, VB ; shift 3 more times
	SHL	VB, VB
	SHL	VB, VB ; VB has dddd0000
	OR	VB, VC ; VB has ddddcccc
; load the timers
	LD	DT, VB
	LD	ST, VB
; wait for the time to be up
WAIT:	LD	V0, DT
	SE	V0, 0
	JP	WAIT
; DT is zero, ST should also be
	JP	TOP

; screen coordinates for first, second digit
FIRST_XY:
	DB	10,10 ; x,y
SECND_XY:
	DB	17,10 ; x,y
	
; Paint a character.
;
; input:
;   V2 has the key code to paint
;   I -> (x, y) coordinates in memory
; changes: V0, V1, I

SHOW_DIGIT:
	LDM	V1 ; pick up v0, v1
	LDC	I, V2 ; I->sprite
	DRAW	V0,V1,5
	RET

