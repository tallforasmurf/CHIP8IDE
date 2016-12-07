; Paints a question mark then waits for
; any keypad key. Paints the key letter.
; Repeats.

	LD I, QUERY ; start with I->?
	LD v9, 16 ; x-coord
	LD vA, 8  ; y-coord
TOP:
; paint the current character
	DRAW v9, VA, 5
; wait for a keypad key
	LD V5, K
; erase the old character by repainting it
	DRAW v9, va, 5
; point I->sprite for keypad key
	LDC I, V5
	JP  TOP ; go draw the new key

; This sprite has to be 5 bytes high because
; all built-in characters are, and "5" is
; coded into the DRAWs above.
; Pretty ugly "?" though.
QUERY:
	DB $..11....
	DB $.1...1..
	DB $....1...
	DB $..1.....
	DB $..1.....

