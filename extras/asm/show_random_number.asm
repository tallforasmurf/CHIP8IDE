;
; This program is from Matthew Mikolay's RetroComputing
; page at http://retro.mattmik.com/index.html.
;
; It demonstrates the use of the random number 
; generator, and the use of the store-BCD instruction
; to convert a binary byte to 3 decimal digits.
;

TOP:	CLS
	; Get a random number in 0..255
	RND V3, #FF
	; point to memory space for 3 digits
	LD I, BCD
	; store 3 digits
	STD V3
	; load the 3 digits into V0, V1, V2
	LDM V2
	; V5 = Y axis for top of digits
	LD	V5, 8
	; V4 = X axis for first digit
	LD V4, 16
	; I -> sprite for digit in V0
	LDC I, V0
	DRAW V4, V5, 5 ; paint it
	; V4 = X coord for digit in V1
	ADD V4, 5
	; I -> sprite for V1 digit
	LDC I, V1
	DRAW V4, V5, 5 ; paint it
	; V4 = X coord for digit in V2
	ADD V4, 5
	; I -> sprite for third digit
	LDC I, V2
	DRAW V4, V5, 5
	; Wait for any key press/release
	LD V3, K
	; repeat
	JP TOP

BCD:	DS	3
