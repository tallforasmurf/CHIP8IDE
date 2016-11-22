; Simple test of using keypad input to control
; a sprite on the screen.
;
; * set x and y to middle of screen
; * draw a splat at x, y
; * wait for a keypad key.
; * erase the splat
; * get x- and y-deltas based on the key.
; * update x and y 
; * repeat
;
; The deltas are based on key position (x,y)
;
;    -2,-2   -1,-2   +1,-2    +2,-2
;    -2,-1   -1,-1   +1,-1    +2,-1
;    -2,+1   -1,+1   +1,+1    +2,+1
;    -2,+2   -1,+2   +1,+2    +2,+2
;
; we use tables indexed by the key code to 
; get these deltas.
;
; registers:
; V5 x-coord
; V6 y-coord
; V7 key input
; V0 work

SCR_WIDTH EQU	64 ; assuming standard screen
SCR_HEIGHT EQU	32

	ld 	V5, SCR_WIDTH/2 ; Initial x-coord
	ld	V6, SCR_HEIGHT/2 ; Initial y-coord
TOP:
	ld	I, SPLAT ; I -> sprite
	DRAW	V5, V6, SPLAT_END - SPLAT
; read a key
	ld	V7, K
; erase the sprite
	DRAW	V5, V6, SPLAT_END-SPLAT
;
; Get X-delta by indexing a table
	LD	I, X_TABLE
	ADD	I, V7 ; index the table
	LDM	V0 ; V0 <- M[I+V7]
	ADD	V5, V0 ; change x-coord
; Ditto for Y
	LD	I, Y_TABLE
	ADD	I, V7
	LDM	V0
	ADD	V6, V0
; and that's it
	JP	TOP ; no, repeat

; the sprite, with a label at the end so the
; byte-count can be given as an expression 
; instead of hard-coded.
SPLAT:
	DB	$1......1
	DB	$.1.1..1.
	DB	$..1..1..
	DB	$1..11..1
	DB	$1..11..1
	DB	$..1..1..
	DB	$.1..1.1.
	DB	$1......1
SPLAT_END:
	
; in these tables we use literal hex values for
; negative binary numbers, e.g. adding #FF is
; effectively adding -1.

X_TABLE: ; x-delta values based on key 0..F
	DB	#FF		; 0
	DB	#FE, #FF, 1 ; 1, 2, 3
	DB	#FE, #FF, 1 ; 4, 5, 6
	DB	#FE, #FF, 1 ; 7, 8, 9
	DB	#FE 		; A
	DB	1 		; B
	DB	2, 2, 2, 2 	; C, D, E, F

Y_TABLE: 	; y-delta values (bearing in mind
		; that y-axis gets bigger going down
	DB	2  			; 0
	DB	#FE, #FE, #FE	; 1, 2, 3
	DB	#FF, #FF, #FF 	; 4, 5, 6
	DB	1, 1, 1 		; 7, 8, 9
	DB	2			; A
	DB	2			; B
	DB	#FE, #FF, 1, 2 	; C, D, E, F
	