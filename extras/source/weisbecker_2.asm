; This is the "rocket program" from the BYTE article
; "An Easy Programming System" by Joseph Weisbecker,
; designer of the VIP and CHIP-8 emulator.
;
; The article ("figure 5") gives the hex digits
; with a pseudocode description. The hex, pseudocode
; and comments from the article are included here
; as comments, with the assembler source. I've
; converted sprite patterns into readable DB's
; and replaced literal addresses with labels.

; Click the F keypad button to launch your rocket.
; Usage note: The "UFO" moves super-fast unless
; you set instructions-per-tick to 10 or less.

; 0200 V1=00 Step 1: Score
	LD V0, 0
; 0202 V2=00         Rocket count
	LD V2, 0
; 0204 V3=38         Score X
	LD v3, #38
; 0206 V4=1B         Score Y
	LD V4, #1B
; 0208 V5=00         UFO X
	LD V5, 0
; 020A V6=08         UFO Y
	LD V6, #08
; 020C I=027E        UFO pattern
	LD I, UFO
; 020E SHOW 3MI@V5V6 UFO
	DRAW V5, V6, 3
; 0210 DO 026A Step 2: Show score
STEP2:	CALL SSS
; 0212 SKIP; V2 NE 09
	SNE V2, #09
; 0214 Step 3: End loop (stop)
; Note: Weisbecker used a hard loop as a way
; of terminating his program, I am substituting
; an EXIT as a nicer way to end it.
;STEP3:	JP STEP3
STEP3:	EXIT

; 0216 V2+01  Step 4:
	ADD V2, 1
; 0218 V8=1A   Rocket Y
	LD V8, #1A
; 021A VA=00
	LD VA, 0
; 021C V7=RND (he doesn't mention the mask)
	RND  V7, #1F
; 021E V7+0F  Rocket X
	ADD  V7, #0F
; 0220 V9=00
	LD V9, 0
; 0222 I=0278 Rocket pattern
	LD I, ROCKET
; 0224 SHOW 6MI@V7V8
	DRAW V7, V8, 6
; 0226 I=027E  Step 5: UFO pattern
STEP5:	LD I, UFO
; 0228 SHOW 3MI@V5V6 Erase UFO
	DRAW V5, V6, 3
; 022A V0=RND (mask again not documented)
	RND V0, #03
; 022C V5=V5+V0  Set VF
	ADD V5, V0
; 022E SHOW 3MI@V5V6
	DRAW V5, V6, 3
; 0230 SKIP; VF EQ 00
	SE VF, 0
; 0232 GO 0262
	JP STEP12
; 0234 V0=0F  Step 6:
STEP6:  	LD V0, 15
; 0236 SKIP; V0 NE KEY
	SKNP V0
; 0238  V9=01
	LD V9, 1
; 023A  SKIP; V9 EQ 01 Step 7:
	SE V9, 1
; 023C GO 0226 Step 5
	JP STEP5
; 023E V0=TIME Step8:
STEP8:	LD V0, DT
; 0240 SKIP; V0 EQ 00
	SE V0, 0
; 0242 GO 0226 Step 5
	JP STEP5
; 0244 I=0278  Step 9: Rocket pattern
	LD I, ROCKET
; 0246 SHOW 6MI@V7V8 Erase rocket
	DRAW V7, V8, 6
; 0248 V8+FF
	ADD V8, #FF
; 024A SHOW 6MI@V7V8
	DRAW V7, V8, 6
; 024C SKIP; VF EQ 00
	SE VF, 0
; 024E GO 0262 Step 12
	JP STEP12
; 0250 V0=03 Step 10:
STEP10:	LD V0, 3
; 0252 TIME=V0
	LD DT, V0
; 0254 SKIP; V8 EQ 00
	SE V8, 0
;
; Either following statement is an error, or the
; comment is wrong! It says, "GO 0226 Step 12"
; but Step 12 is at 0262, see for example the
; instructionat 024E just above. However, STEP 5
; is at 0226. Does he want to go to STEP12 or STEP5?
; The instruction in hex is 1226, which is STEP5.
; 0226 ... 0262 ... the danger of coding in hex!
;
; 0256 GO 0226 Step 12
	JP #0226
; 0258 DO 026A  Step 11: Erase score
STEP11:	CALL SSS
; 025A I=0278 Rocket pattern
	LD I, ROCKET
; 025C SHOW 6MI@V7V8 Erase rocket
	DRAW V7, V8, 6
; 025E V1=V1+VA  Score+VA
	ADD V1, VA
; 0260 GO 0210
	JP STEP2

; 0262 VA=01 Step 12:
STEP12:	LD VA, 1
; 0264 V0=3
	LD V0, 3
; 0266 TONE=V0
	LD ST, V0
; 0268 GO 0258
	JP STEP11

; 026A I=02A0  SSS: 3 byte work area
SSS:	LD I, SCORE
; 026C MI=V1 (3DD)
	STD V1
; 026E I=02A2 Least significant digit
	LD I, SCORE+2
; 0270 V0:V0=MI
	LDM V0
; 0272 I=V0 (LSDP)
	LDC I, V0
; 0274 SHOW 5MI@V3V4
	DRAW V3, V4, 5
; 0276 RET
	RET

ROCKET: ; rocket pattern
	DB $..1.....
	DB $.111....
	DB $.111....
	DB $11111...
	DB $11.11...
	DB $1...1...

UFO: ; UFO Pattern
	DB $.11111..
	DB $11.1.11.
	DB $.11111..
	DB $........

; 02A0 no comment - undefined scratch area for
; decimal digit deposition...
SCORE:	DS 3