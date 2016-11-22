; This is a version of the KALEIDOSCOPE program for
; CHIP-8, with a small modification to make it use the
; larger SCHIP screen.


	HIGH		; start out with the 128x64 screen
LBL0200:
	LD V0, #00
	LD V3, #80 ; index to buffer 0280..02FF
	LD V1, #3F ; half the screen width - 1
	LD V2, #1F ; half the screen height - 1

LBL0208:
	CALL QUADRANTS	; Display the pattern as it is
	LD I, LBL0200
	ADD I, V3		; I-> buffer, M[200+v3]

	LD V0, K		; Read a key and..
	STM V0		; ..store in buffer *I

	SNE V0, #00		; If the key was zero, 
	JP LBL021C		; .. go finish up

				; key is not zero so get ready
	ADD V3, #01	 	; to store it: incr V3,
	SE V3, #00		; if it has not overflowed,
	JP LBL0208		; .. loop for another key
				; else fall through to...

; Either key 0 hit or v3 passed 255, filling buffer.
; Start replicating and expanding the design now
; in memory[200..?]

LBL021C:
	LD V3, #80		; back to start of buffer

LBL021E:
	LD I, LBL0200
	ADD I, V3		; I->next key code
	LDM V0		; v0 = next key code
	SNE V0, #00		; if is zero,
	JP LBL021C		; ..start over at V3=80

	ADD V3, #01		; increment v3 and check,
	SNE V3, #00		; is it off the end (>FF)?
	JP LBL021C		; if so, restart at #280

	CALL QUADRANTS	; draw the pattern and
	JP LBL021E		; ..get the next code
;
; "The subroutine at 0232-0274 causes your pattern
; to be duplicated in the four quadrants of the screen."
;
; Input:
;	v0 has a key code 2,4,6,8 or 0
;	V1 has an X-coord
;	V2 has a Y-coord
;
; Changes:
;	V1, V2, VA, VB
;
QUADRANTS:
	SNE V0, #02		; if V0 == 2,
	ADD V2, #FF		; 	Y_coord -= 1
	SNE V0, #04		; if V0 == 4,
	ADD V1, #FF		; 	X_coord -= 1
	SNE V0, #06 	; if V0 == 6,
	ADD V1, #01		; 	X_coord += 1
	SNE V0, #08		; if V0 == 8,
	ADD V2, #01		; 	Y_coord += 1

	LD I, ONE_SPOT_SPRITE	; I-> lonely DB #80
;
; V1 can range from 0 to 7F (0-127)
; and V2 from 0 to 3F (0-63).
;
; V1 can contain from $.... .... to $.111 1111
; V1 AND $11.. .... results in either #00 or #40
; where 0 means, V1 indexes the left side of screen,
; #40 means, indexes the right side.
;
	LD VA, #C0		
	AND VA, V1		; VA = left or right
;
; V1 AND $..11 1111 results in 0..3F
;
	LD VB, #3F		; V1 gets X_coord for left or
	AND V1, VB		; right half

	SE VA, #00		; if it is #40==Right side,
	ADD V2, #01		; .. Y_coord += 1

; V2 can be from 00..3F
; AND that with #E0 you get either #20 for bottom half,
; or #00 for top half.

	LD VA, #E0
	AND VA, V2		; VA = $10 for bottom, 0 for top
	LD VB, #1F		; V2 gets Y_coord for either
	AND V2, VB		; upper or lower

	SE VA, #00 		; if it is $20==bottom half,
	ADD V1, #01		; .. X_coord += 1

	LD VB, #3F		; in case the increment flipped it,
	AND V1, VB		; force V1 back to left side

	DRAW V1, V2, 1 	; draw in the upper left quad
	LD VA, V1		; save the X_coord

	LD VB, #3F		; get the 64-complement of the
	SUB VB, V2		; Y_coord in VB

	DRAW VA, VB, 1	; draw the lower left quad

	LD VA, #7F		; get the 128-complement of the
	SUB VA, V1		; X_coord in VA
	DRAW VA, VB, 1	; draw the lower right

	LD VB, V2		; recover original Y_coord
	DRAW VA, VB, 1	; draw the upper right

	RET

; Is this ever referenced? I think not.
	DB #01

; This one-pixel, one-byte sprite is used to draw a
; single pixel in 4 quadrants of the screen.

ONE_SPOT_SPRITE:
	DB #80
;
; The user key-codes are stored at #200+V3 which
; ranges from #80..#FF. So what happens here in the
; gap from #278..#27F ?
;

