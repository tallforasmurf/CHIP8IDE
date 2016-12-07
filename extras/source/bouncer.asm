;
; Bouncer
;
; Draw a 4-pixel "ball" in the middle of the screen.
; Set some initial x- and y-increments
; Set delay count (determines speed)
;
; Note: DELAY=1 demonstrates smooth animation at
; ~60fps -- for a very small sprite anyway.
;
; loop:
;	put delay count in DT
;	wait for it to be 0
;	repaint the ball to erase it
;	increment the x- and y-axes
;	for each axis,
; 		if the ball has reached a border
;		negate the increment and reapply it
;		put a small value in the ST
;	paint the ball
;	repeat from loop
;
; registers:
; v0, v1, v2, vf - work
;
; vC x-increment
; vD x-coord
; vE x-limit (x from 0..vE)
;
; v9 y-increment
; vA y-coord
; vB y-limit (y from 0..vB)
; 

SCR_WIDTH	EQU 64 ; assuming old
SCR_HEIGHT	EQU 32 ; ..screen size

DELAY	EQU	1 ; 2-tick delay, 30fps about

	ld	vC, 1 ; initial x-incr
	ld	vE, SCR_WIDTH-4 ; x-limit

	ld	v9, 1 ; initial y-incr
	ld	vB, SCR_HEIGHT-1

; set starting coordinates somewhere around
; the middle of the screen.
	ld	vD, (SCR_WIDTH/2)-2
	rnd	v0,3
	add	vD, v0
	ld	vA, (SCR_HEIGHT/2)-1
	rnd	v0,3
	add	VA, v0

LOOP:
	ld	I, BALL
	DRAW	VD, VA, 2	; draw the ball at new spot

	ld	v0, DELAY
	ld	DT, v0
WAIT:
	ld	v0, DT
	se	v0, 0
	jp	WAIT

	LD	I, BALL
	DRAW	VD, VA, 2 ; erase the ball

INCR_X:
	add	vD, vC ; add plus/minus increment
; We let x go negative but if we test #FF
; against the right-side limit, it looks like
; going to far. So skip this test for X<0
	ld	v0, vD
	ld	v1, #80
	and	v0, v1
	se	v0, 0
	jp	TEST_X_0

; X is positive, test it against the +limit
	ld	v0, vD
	sub	v0, vE
; the logic here is, if vD has gone past
; the limit in vE, the above subtract does
; NOT produce a borrow (62-63:borrow, but
; 63-63 or 64-63, no borrow). If NO
; borrow, vF==01, skip the jump.
	sne	vF, 0 ; skip if no borrow
	jp	TEST_X_0 ; x not over max, continue
	
; X has hit a limit. flip its increment from
; plus to minus or vice versa.

FIX_X:
	ld	v2, vC
	call	NEGATE ; negate the x incr
	ld	vC, v2
	jp	INCR_X ; and try again

; X has not gone too far right, what about
; too far left?
TEST_X_0:
	ld	v0, vD
	add	v0, 3
; here the logic is, we can let x go to -3
; (because of 3 black pixels left side of the
; sprite, and the screen wraps around) so we
; add 3 and if the result has the high bit on
; (#FD+3 = 00, #FC+3 = FF) we are too far left.
; So if the high bit IS on, jump back and
; invert the increment and try again.
	ld	v1, #80
	and	v0, v1 ; leaves high bit set
	se	v0, 0	; if high bit on do not skip
	jp	FIX_X ; ..turn X around

; ditto ditto for Y - could these be factored
; into a subroutine?
INCR_Y:
	add	vA, v9
	ld	v0, vA
	sub	v0, vB
	sne	vF, 0 ; skip if no borrow
	jp	TEST_Y_0 ; vF==0, borrow, ok
FIX_Y:
	ld	v2, V9
	call	NEGATE
	ld	v9, v2
	jp	INCR_Y
TEST_Y_0:
; We cannot let Y go negative because there
; are no unpainted pixels at the top of the
; sprite. So, if the high bit of Y is on,
; time to reverse the Y direction.
	ld	v0, vA
	ld	v1, #80
	and	v0, v1 ; isolate high bit
	se	v0, 0 ; skip on non-negative
	jp	FIX_Y
; both coordinates are ok, loop
	jp	LOOP

; Arithmetically negate the value in v2.
; To negate a signed binary value, invert
; all the bits and add 1.
;
; This is only used when we have hit a wall
; and need to reverse at least one direction.
; So it is a convenient place to also trigger
; a beep noise by setting a small value in ST.
;
; in/out v2
; changes v0
; changes ST

BEEP_LEN	EQU	2

NEGATE:
	ld	v0, #FF
	xor	v0, v2
	add	v0, 1
	ld	v2, v0
	ld	v0, BEEP_LEN
	ld	ST, v0
	RET

BALL:
	db $...11...
	db $...11...
