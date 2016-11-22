;
; Scroll Test.
;
; Paints a rocket ship in the middle of the
; screen. Then waits for a keypad key.
; When the key is 4, scroll left.
; When the key is 6, scroll right.
; when the key is 0, scroll down.

KEY_LEFT EQU 4
KEY_RIGHT EQU 6
KEY_DOWN EQU 0

	LD I, ROCKET
	LD v9, 16 ; x-coord
	LD vA, 8  ; y-coord
	DRAW v9, va, ROCKET_END-ROCKET
TOP:
; wait for a keypad key
	LD v5, K
; decode the key
	SNE v5, KEY_LEFT
	JP  LEFT
	SNE v5, KEY_RIGHT
	JP  RIGHT
	SNE v5, KEY_DOWN
	JP  DOWN
; none of the above
	JP WAIT

LEFT:	SCL
	JP WAIT

RIGHT:	SCR
	JP WAIT

DOWN:      SCD 1

; wait here while the key remains pressed
WAIT:	SKP v5   ; is that key still down?
	JP  TOP  ; no, carry on
	JP WAIT  ; yup, try again

ROCKET:
	DB $...1....
	DB $..111...
	DB $..111...
	DB $..111...
	DB $.11.11..
	DB $1.....1.
ROCKET_END: ; for expression

