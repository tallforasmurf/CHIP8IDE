; This is the disassembled source for JOUST23
; from David ; Winter's collection at
; http://www.pong-story.com/chip8/
;
; It seems to run but is not very responsive.
; Click "A" to start a game.
; Click "3" to move left
; Click "C" to move right
; Click and hold "A" to climb.
;

LBL004A EQU #004a ; unmatched label
LBL0076 EQU #0076 ; unmatched label
LBL0AA0 EQU #0aa0 ; unmatched label
LBL0AC6 EQU #0ac6 ; unmatched label
LBL0BB6 EQU #0bb6 ; unmatched label
LBL0C28 EQU #0c28 ; unmatched label
LBL0E00 EQU #0e00 ; unmatched label
	JP LBL020E ; 120E
	CALL LBL004A ; 204A
	LD VF, #75 ; 6F75
	ADD V3, #74 ; 7374
	CALL LBL0076 ; 2076
	SE V2, #2E ; 322E
	SE V3, #00 ; 3300
LBL020E: HIGH ; 00FF
	CALL LBL08F0 ; 28F0
LBL0212: LD V0, #00 ; 6000
	LD I, LBL0A5A ; AA5A
	STM V0 ; F055
	LD V8, #00 ; 6800
	LD V9, #03 ; 6903
	LD VC, #00 ; 6C00
LBL021E: LD VD, #0F ; 6D0F
	CALL LBL029E ; 229E
	CLS ; 00E0
	LD VA, #02 ; 6A02
	ADD VC, #01 ; 7C01
	LD VD, #07 ; 6D07
	SUB VD, VC ; 8DC5
	SNE VF, #00 ; 4F00
	JP LBL024E ; 124E
	SNE VC, #04 ; 4C04
	LD V8, #01 ; 6801
	LD VB, VC ; 8BC0
	ADD VB, #01 ; 7B01
LBL0238: CALL LBL0748 ; 2748
	LD VE, #1B ; 6E1B
	LD VD, #09 ; 6D09
	SUB VD, VC ; 8DC5
	SNE VF, #00 ; 4F00
	JP LBL0254 ; 1254
	LDH I, VC ; FC30
	LD VD, #3C ; 6D3C
	DRAW VD, VE, 10 ; DDEA
	CALL LBL0750 ; 2750
	JP LBL026A ; 126A
LBL024E: LD VB, #08 ; 6B08
	LD V8, #02 ; 6802
	JP LBL0238 ; 1238
LBL0254: LD I, LBL0AB0 ; AAB0
	STD VC ; FC33
	LDM V2 ; F265
	LD VD, #37 ; 6D37
	LDH I, V1 ; F130
	DRAW VD, VE, 10 ; DDEA
	LD VD, #41 ; 6D41
	LDH I, V2 ; F230
	DRAW VD, VE, 10 ; DDEA
	CALL LBL0750 ; 2750
	JP LBL026A ; 126A
LBL026A: LD VD, #07 ; 6D07
	AND VD, VC ; 8DC2
	SNE VD, #07 ; 4D07
	JP LBL0950 ; 1950
	CALL LBL084C ; 284C
	CALL LBL0770 ; 2770
	CALL LBL05F8 ; 25F8
	SE VB, #00 ; 3B00
	CALL LBL05F0 ; 25F0
	LD VD, #0F ; 6D0F
	CALL LBL029E ; 229E
LBL0280: CALL LBL02A8 ; 22A8
	SNE V6, #DD ; 46DD
	JP LBL06B0 ; 16B0
	SNE VA, #00 ; 4A00
	JP LBL021E ; 121E
	CALL LBL02FA ; 22FA
	SE V8, #00 ; 3800
	CALL LBL04BC ; 24BC
	LD VD, #05 ; 6D05
	SNE V8, #00 ; 4800
	CALL LBL029E ; 229E
	LD VD, #03 ; 6D03
	SNE V8, #01 ; 4801
	CALL LBL029E ; 229E
	JP LBL0280 ; 1280
LBL029E: LD DT, VD ; FD15
LBL02A0: LD VD, DT ; FD07
	SE VD, #00 ; 3D00
	JP LBL02A0 ; 12A0
	RET ; 00EE
LBL02A8: LD I, LBL0A82 ; AA82
	LDM V5 ; F565
	CALL LBL04A0 ; 24A0
	LD V2, #00 ; 6200
	LD VD, #0A ; 6D0A
	SKNP VD ; EDA1
	CALL LBL049C ; 249C
	LD VD, #03 ; 6D03
	SKNP VD ; EDA1
	CALL LBL0490 ; 2490
	LD VD, #0C ; 6D0C
	SKNP VD ; EDA1
	CALL LBL0496 ; 2496
	CALL LBL02CE ; 22CE
	SNE V6, #DD ; 46DD
	RET ; 00EE
	SE VF, #00 ; 3F00
	CALL LBL0516 ; 2516
	RET ; 00EE
LBL02CE: CALL LBL0782 ; 2782
	CALL LBL07EC ; 27EC
LBL02D2: LD VD, V0 ; 8D00
	LD VE, V1 ; 8E10
	ADD V0, V2 ; 8024
	ADD V1, V3 ; 8134
	LD I, LBL0A62 ; AA62
	ADD I, V5 ; F51E
	LD V5, #7F ; 657F
	AND V0, V5 ; 8052
	LD V5, V4 ; 8540
	LD V6, V0 ; 8600
	LD V7, V1 ; 8710
	DRAW VD, VE, 8 ; DDE8
	LD I, LBL0A62 ; AA62
	ADD I, V4 ; F41E
	DRAW V0, V1, 8 ; D018
	SNE V1, #38 ; 4138
	LD V6, #DD ; 66DD
	LD I, LBL0A82 ; AA82
	STM V5 ; F555
	RET ; 00EE
LBL02FA: SNE VA, #01 ; 4A01
	JP LBL0316 ; 1316
	SNE VA, #02 ; 4A02
	JP LBL030E ; 130E
	SNE VA, #03 ; 4A03
	JP LBL03AE ; 13AE
	SNE VA, #04 ; 4A04
	JP LBL03B4 ; 13B4
	SNE VA, #05 ; 4A05
	JP LBL03BA ; 13BA
LBL030E: CALL LBL0316 ; 2316
	SNE VA, #02 ; 4A02
	CALL LBL0368 ; 2368
	RET ; 00EE
LBL0316: LD I, LBL0A88 ; AA88
	LDM V5 ; F565
	RND VD, #03 ; CD03
	SNE VD, #00 ; 4D00
	CALL LBL04A4 ; 24A4
	CALL LBL032A ; 232A
	CALL LBL037A ; 237A
	SE VF, #00 ; 3F00
	JP LBL04E8 ; 14E8
	RET ; 00EE
LBL032A: LD VD, V6 ; 8D60
	SUB VD, V0 ; 8D05
	SNE VF, #00 ; 4F00
	SUBN VD, VF ; 8DF7
	LD VE, #10 ; 6E10
	SUB VE, VD ; 8ED5
	SNE VF, #00 ; 4F00
	RET ; 00EE
	LD VD, V7 ; 8D70
	SUB VD, V1 ; 8D15
	SNE VF, #00 ; 4F00
	SUBN VD, VF ; 8DF7
	LD VE, #0C ; 6E0C
	SUB VE, VD ; 8ED5
	SNE VF, #00 ; 4F00
	RET ; 00EE
	LD VD, V6 ; 8D60
	SUB VD, V0 ; 8D05
	SNE VF, #00 ; 4F00
	CALL LBL0490 ; 2490
	SE VF, #00 ; 3F00
	CALL LBL0496 ; 2496
	LD VD, V7 ; 8D70
	SUB VD, V1 ; 8D15
	SE VF, #00 ; 3F00
	CALL LBL04A0 ; 24A0
	SNE VF, #00 ; 4F00
	CALL LBL049C ; 249C
	SNE V1, V7 ; 9170
	CALL LBL049C ; 249C
	RET ; 00EE
LBL0368: LD I, LBL0A8E ; AA8E
	LDM V5 ; F565
	RND VD, #01 ; CD01
	SNE VD, #00 ; 4D00
	CALL LBL04A4 ; 24A4
	CALL LBL0382 ; 2382
	SE VF, #00 ; 3F00
	JP LBL04F0 ; 14F0
	RET ; 00EE
LBL037A: CALL LBL038A ; 238A
	LD I, LBL0A88 ; AA88
	STM V5 ; F555
	RET ; 00EE
LBL0382: CALL LBL038A ; 238A
	LD I, LBL0A8E ; AA8E
	STM V5 ; F555
	RET ; 00EE
LBL038A: CALL LBL0782 ; 2782
	CALL LBL07EC ; 27EC
	SNE V1, #34 ; 4134
	CALL LBL049C ; 249C
LBL0392: LD VD, V0 ; 8D00
	LD VE, V1 ; 8E10
	ADD V0, V2 ; 8024
	ADD V1, V3 ; 8134
	LD I, LBL0A72 ; AA72
	ADD I, V5 ; F51E
	LD V5, #7F ; 657F
	AND V0, V5 ; 8052
	LD V5, V4 ; 8540
	DRAW VD, VE, 8 ; DDE8
	LD I, LBL0A72 ; AA72
	ADD I, V4 ; F41E
	DRAW V0, V1, 8 ; D018
	RET ; 00EE
LBL03AE: CALL LBL0316 ; 2316
	CALL LBL03BA ; 23BA
	RET ; 00EE
LBL03B4: CALL LBL040E ; 240E
	CALL LBL03BA ; 23BA
	RET ; 00EE
LBL03BA: LD I, LBL0A94 ; AA94
	LDM V4 ; F465
	SNE V4, #02 ; 4402
	JP LBL03CE ; 13CE
	LD V2, #00 ; 6200
	CALL LBL0440 ; 2440
	CALL LBL047C ; 247C
	LD I, LBL0A94 ; AA94
	STM V4 ; F455
	RET ; 00EE
LBL03CE: ADD V2, #01 ; 7201
	SNE V2, #08 ; 4208
	JP LBL03DA ; 13DA
	LD I, LBL0A94 ; AA94
	STM V4 ; F455
	RET ; 00EE
LBL03DA: LD I, LBL0AC2 ; AAC2
	DRAW V0, V1, 4 ; D014
	SNE VA, #04 ; 4A04
	JP LBL03EA ; 13EA
	SNE VA, #03 ; 4A03
	JP LBL0400 ; 1400
	LD VA, #00 ; 6A00
	RET ; 00EE
LBL03EA: LD I, LBL0A9A ; AA9A
	LDM V4 ; F465
	LD I, LBL0A94 ; AA94
	STM V4 ; F455
	SNE VB, #00 ; 4B00
	LD VA, #05 ; 6A05
	SNE VB, #00 ; 4B00
	RET ; 00EE
	CALL LBL05F8 ; 25F8
	LD VA, #03 ; 6A03
	RET ; 00EE
LBL0400: SNE VB, #00 ; 4B00
	LD VA, #01 ; 6A01
	SNE VB, #00 ; 4B00
	RET ; 00EE
	CALL LBL05F0 ; 25F0
	LD VA, #02 ; 6A02
	RET ; 00EE
LBL040E: LD I, LBL0A9A ; AA9A
	LDM V4 ; F465
	SNE V4, #02 ; 4402
	JP LBL0422 ; 1422
	LD V2, #00 ; 6200
	CALL LBL0440 ; 2440
	CALL LBL047C ; 247C
	LD I, LBL0A9A ; AA9A
	STM V4 ; F455
	RET ; 00EE
LBL0422: ADD V2, #01 ; 7201
	SNE V2, #08 ; 4208
	JP LBL042E ; 142E
	LD I, LBL0A9A ; AA9A
	STM V4 ; F455
	RET ; 00EE
LBL042E: LD I, LBL0AC2 ; AAC2
	DRAW V0, V1, 4 ; D014
	SNE VB, #00 ; 4B00
	JP LBL043C ; 143C
	CALL LBL05F8 ; 25F8
	LD VA, #03 ; 6A03
	RET ; 00EE
LBL043C: LD VA, #05 ; 6A05
	RET ; 00EE
LBL0440: SNE V1, #18 ; 4118
	JP LBL0450 ; 1450
	SNE V1, #0C ; 410C
	JP LBL0466 ; 1466
	SNE V1, #24 ; 4124
	JP LBL0466 ; 1466
	LD V3, #01 ; 6301
	RET ; 00EE
LBL0450: CALL LBL07AC ; 27AC
	SE V3, #00 ; 3300
	RET ; 00EE
	LD VD, #01 ; 6D01
	LD ST, VD ; FD18
	LD V3, #FD ; 63FD
	SNE V4, #00 ; 4400
	LD V2, #FE ; 62FE
	SNE V4, #01 ; 4401
	LD V2, #02 ; 6202
	RET ; 00EE
LBL0466: CALL LBL07BE ; 27BE
	SE V3, #00 ; 3300
	RET ; 00EE
	LD VD, #01 ; 6D01
	LD ST, VD ; FD18
	LD V3, #FD ; 63FD
	SNE V4, #00 ; 4400
	LD V2, #FE ; 62FE
	SNE V4, #01 ; 4401
	LD V2, #02 ; 6202
	RET ; 00EE
LBL047C: LD VD, V0 ; 8D00
	LD VE, V1 ; 8E10
	ADD V0, V2 ; 8024
	ADD V1, V3 ; 8134
	LD I, LBL0AC2 ; AAC2
	DRAW VD, VE, 4 ; DDE4
	DRAW V0, V1, 4 ; D014
	SNE V1, #38 ; 4138
	LD V4, #02 ; 6402
	RET ; 00EE
LBL0490: LD V4, #08 ; 6408
	LD V2, #FC ; 62FC
	RET ; 00EE
LBL0496: LD V4, #00 ; 6400
	LD V2, #04 ; 6204
	RET ; 00EE
LBL049C: LD V3, #FE ; 63FE
	RET ; 00EE
LBL04A0: LD V3, #02 ; 6302
	RET ; 00EE
LBL04A4: RND VD, #01 ; CD01
	LD ST, VD ; FD18
	SNE VD, #00 ; 4D00
	CALL LBL0490 ; 2490
	SNE VD, #01 ; 4D01
	CALL LBL0496 ; 2496
	RND VD, #01 ; CD01
	SNE VD, #00 ; 4D00
	CALL LBL04A0 ; 24A0
	SNE VD, #01 ; 4D01
	CALL LBL049C ; 249C
	RET ; 00EE
LBL04BC: RND VD, #03 ; CD03
	SE VD, #00 ; 3D00
	RET ; 00EE
	LD I, LBL0AC0 ; AAC0
	LDM V1 ; F165
	LD VD, #3B ; 6D3B
	LD I, LBL0ABA ; AABA
	DRAW V0, VD, 5 ; D0D5
	ADD V0, V1 ; 8014
	SNE V0, #08 ; 4008
	CALL LBL04DC ; 24DC
	SNE V0, #70 ; 4070
	CALL LBL04E2 ; 24E2
	LD I, LBL0AC0 ; AAC0
	STM V1 ; F155
	RET ; 00EE
LBL04DC: LD V0, #10 ; 6010
	LD V1, #08 ; 6108
	RET ; 00EE
LBL04E2: LD V0, #68 ; 6068
	LD V1, #F8 ; 61F8
	RET ; 00EE
LBL04E8: CALL LBL04F8 ; 24F8
	SNE VF, #00 ; 4F00
	JP LBL0592 ; 1592
	RET ; 00EE
LBL04F0: CALL LBL04F8 ; 24F8
	SNE VF, #00 ; 4F00
	JP LBL05CE ; 15CE
	RET ; 00EE
LBL04F8: LD VD, V6 ; 8D60
	SUB VD, V0 ; 8D05
	SNE VF, #00 ; 4F00
	SUBN VD, VF ; 8DF7
	LD VE, #08 ; 6E08
	SUB VD, VE ; 8DE5
	SE VF, #00 ; 3F00
	RET ; 00EE
	LD VD, V7 ; 8D70
	SUB VD, V1 ; 8D15
	SNE VF, #00 ; 4F00
	SUBN VD, VF ; 8DF7
	LD VE, #08 ; 6E08
	SUB VD, VE ; 8DE5
	RET ; 00EE
LBL0516: SNE VA, #02 ; 4A02
	JP LBL0564 ; 1564
	SNE VA, #01 ; 4A01
	JP LBL0592 ; 1592
	SNE VA, #04 ; 4A04
	JP LBL0528 ; 1528
	SNE VA, #05 ; 4A05
	JP LBL053A ; 153A
	JP LBL0552 ; 1552
LBL0528: LD I, LBL0A94 ; AA94
	LDM V4 ; F465
	CALL LBL0576 ; 2576
	SNE VF, #00 ; 4F00
	JP LBL0546 ; 1546
	CALL LBL0584 ; 2584
	SNE VF, #00 ; 4F00
	JP LBL0546 ; 1546
	JP LBL053A ; 153A
LBL053A: CALL LBL0720 ; 2720
	CALL LBL0702 ; 2702
	CALL LBL0702 ; 2702
	LD I, LBL0A94 ; AA94
	LDM V4 ; F465
	JP LBL03DA ; 13DA
LBL0546: CALL LBL0720 ; 2720
	CALL LBL0702 ; 2702
	CALL LBL0702 ; 2702
	LD I, LBL0A9A ; AA9A
	LDM V4 ; F465
	JP LBL042E ; 142E
LBL0552: LD I, LBL0A88 ; AA88
	LDM V5 ; F565
	CALL LBL0576 ; 2576
	SNE VF, #00 ; 4F00
	JP LBL053A ; 153A
	CALL LBL0584 ; 2584
	SNE VF, #00 ; 4F00
	JP LBL053A ; 153A
	JP LBL0592 ; 1592
LBL0564: LD I, LBL0A88 ; AA88
	LDM V5 ; F565
	CALL LBL0576 ; 2576
	SNE VF, #00 ; 4F00
	JP LBL05CE ; 15CE
	CALL LBL0584 ; 2584
	SNE VF, #00 ; 4F00
	JP LBL05CE ; 15CE
	JP LBL0592 ; 1592
LBL0576: LD VD, V6 ; 8D60
	SUB VD, V0 ; 8D05
	SNE VF, #00 ; 4F00
	SUBN VD, VF ; 8DF7
	LD VE, #08 ; 6E08
	SUB VE, VD ; 8ED5
	RET ; 00EE
LBL0584: LD VD, V7 ; 8D70
	SUB VD, V1 ; 8D15
	SNE VF, #00 ; 4F00
	SUBN VD, VF ; 8DF7
	LD VE, #08 ; 6E08
	SUB VE, VD ; 8ED5
	RET ; 00EE
LBL0592: LD I, LBL0A88 ; AA88
	LDM V5 ; F565
	SNE V7, V1 ; 9710
	JP LBL0662 ; 1662
	LD VD, V7 ; 8D70
	SUB VD, V1 ; 8D15
	SE VF, #00 ; 3F00
	JP LBL05EC ; 15EC
	CALL LBL070C ; 270C
	LD I, LBL0A72 ; AA72
	ADD I, V5 ; F51E
	DRAW V0, V1, 8 ; D018
	SNE VA, #03 ; 4A03
	JP LBL05BA ; 15BA
	SNE VA, #02 ; 4A02
	JP LBL05C0 ; 15C0
	SNE VA, #01 ; 4A01
	LD VA, #05 ; 6A05
	CALL LBL0640 ; 2640
	RET ; 00EE
LBL05BA: LD VA, #04 ; 6A04
	CALL LBL0648 ; 2648
	RET ; 00EE
LBL05C0: CALL LBL0640 ; 2640
	LD I, LBL0A8E ; AA8E
	LDM V5 ; F565
	LD I, LBL0A88 ; AA88
	STM V5 ; F555
	LD VA, #03 ; 6A03
	RET ; 00EE
LBL05CE: LD I, LBL0A8E ; AA8E
	LDM V5 ; F565
	SNE V7, V1 ; 9710
	JP LBL0678 ; 1678
	LD VD, V7 ; 8D70
	SUB VD, V1 ; 8D15
	SE VF, #00 ; 3F00
	JP LBL05EC ; 15EC
	CALL LBL070C ; 270C
	LD I, LBL0A72 ; AA72
	ADD I, V5 ; F51E
	DRAW V0, V1, 8 ; D018
	LD VA, #03 ; 6A03
	CALL LBL0640 ; 2640
	RET ; 00EE
LBL05EC: LD V6, #DD ; 66DD
	RET ; 00EE
LBL05F0: CALL LBL0600 ; 2600
	LD I, LBL0A8E ; AA8E
	STM V5 ; F555
	RET ; 00EE
LBL05F8: CALL LBL0600 ; 2600
	LD I, LBL0A88 ; AA88
	STM V5 ; F555
	RET ; 00EE
LBL0600: CALL LBL061A ; 261A
	ADD VB, #FF ; 7BFF
	CALL LBL049C ; 249C
	RND VD, #01 ; CD01
	SE VD, #01 ; 3D01
	CALL LBL0490 ; 2490
	SE VD, #00 ; 3D00
	CALL LBL0496 ; 2496
	LD I, LBL0A72 ; AA72
	ADD I, V4 ; F41E
	DRAW V0, V1, 8 ; D018
	LD V5, V4 ; 8540
	RET ; 00EE
LBL061A: RND VD, #03 ; CD03
	SNE VD, #00 ; 4D00
	JP LBL063A ; 163A
	SNE VD, #01 ; 4D01
	JP LBL0634 ; 1634
	SNE VD, #02 ; 4D02
	JP LBL062E ; 162E
	LD V0, #78 ; 6078
	LD V1, #34 ; 6134
	RET ; 00EE
LBL062E: LD V0, #40 ; 6040
	LD V1, #20 ; 6120
	RET ; 00EE
LBL0634: LD V0, #40 ; 6040
	LD V1, #08 ; 6108
	RET ; 00EE
LBL063A: LD V0, #08 ; 6008
	LD V1, #14 ; 6114
	RET ; 00EE
LBL0640: CALL LBL0650 ; 2650
	LD I, LBL0A94 ; AA94
	STM V4 ; F455
	RET ; 00EE
LBL0648: CALL LBL0650 ; 2650
	LD I, LBL0A9A ; AA9A
	STM V4 ; F455
	RET ; 00EE
LBL0650: ADD V1, #08 ; 7108
	LD VD, #37 ; 6D37
	SUB VD, V1 ; 8D15
	SNE VF, #00 ; 4F00
	LD V1, #37 ; 6137
	RND V4, #01 ; C401
	LD I, LBL0AC2 ; AAC2
	DRAW V0, V1, 4 ; D014
	RET ; 00EE
LBL0662: CALL LBL068E ; 268E
	SE VF, #00 ; 3F00
	JP LBL0670 ; 1670
	CALL LBL0496 ; 2496
	CALL LBL037A ; 237A
	CALL LBL037A ; 237A
	JP LBL06A4 ; 16A4
LBL0670: CALL LBL0490 ; 2490
	CALL LBL037A ; 237A
	CALL LBL037A ; 237A
	JP LBL0698 ; 1698
LBL0678: CALL LBL068E ; 268E
	SE VF, #00 ; 3F00
	JP LBL0686 ; 1686
	CALL LBL0496 ; 2496
	CALL LBL0382 ; 2382
	CALL LBL0382 ; 2382
	JP LBL06A4 ; 16A4
LBL0686: CALL LBL0490 ; 2490
	CALL LBL0382 ; 2382
	CALL LBL0382 ; 2382
	JP LBL0698 ; 1698
LBL068E: LD VD, #03 ; 6D03
	LD ST, VD ; FD18
	LD VD, V6 ; 8D60
	SUB VD, V0 ; 8D05
	RET ; 00EE
LBL0698: LD I, LBL0A82 ; AA82
	LDM V5 ; F565
	CALL LBL0496 ; 2496
	CALL LBL02CE ; 22CE
	CALL LBL02CE ; 22CE
	RET ; 00EE
LBL06A4: LD I, LBL0A82 ; AA82
	LDM V5 ; F565
	CALL LBL0490 ; 2490
	CALL LBL02CE ; 22CE
	CALL LBL02CE ; 22CE
	RET ; 00EE
LBL06B0: CALL LBL070C ; 270C
	CALL LBL0702 ; 2702
	CALL LBL0716 ; 2716
	LD VD, #0A ; 6D0A
	CALL LBL029E ; 229E
	ADD V9, #FF ; 79FF
	SNE V9, #00 ; 4900
	JP LBL06DA ; 16DA
	SNE VA, #01 ; 4A01
	ADD VB, #01 ; 7B01
	SNE VA, #03 ; 4A03
	ADD VB, #01 ; 7B01
	SNE VA, #02 ; 4A02
	ADD VB, #02 ; 7B02
	LD VA, #02 ; 6A02
	SNE VB, #00 ; 4B00
	JP LBL021E ; 121E
	LD VA, #02 ; 6A02
	SNE VB, #01 ; 4B01
	LD VA, #01 ; 6A01
	JP LBL026A ; 126A
LBL06DA: CALL LBL06E4 ; 26E4
	CLS ; 00E0
	CALL LBL072A ; 272A
	CALL LBL090C ; 290C
	JP LBL0212 ; 1212
LBL06E4: LD VD, #0C ; 6D0C
	LD ST, VD ; FD18
	LD VD, #18 ; 6D18
	CALL LBL029E ; 229E
	CALL LBL070C ; 270C
	CALL LBL070C ; 270C
	CALL LBL0716 ; 2716
	CALL LBL0716 ; 2716
	LD VD, #20 ; 6D20
	CALL LBL029E ; 229E
	CALL LBL0716 ; 2716
	CALL LBL0716 ; 2716
	LD VD, #20 ; 6D20
	CALL LBL029E ; 229E
	RET ; 00EE
LBL0702: LD VD, #02 ; 6D02
	LD ST, VD ; FD18
	LD VD, #05 ; 6D05
	CALL LBL029E ; 229E
	RET ; 00EE
LBL070C: LD VD, #04 ; 6D04
	LD ST, VD ; FD18
	LD VD, #0A ; 6D0A
	CALL LBL029E ; 229E
	RET ; 00EE
LBL0716: LD VD, #08 ; 6D08
	LD ST, VD ; FD18
	LD VD, #14 ; 6D14
	CALL LBL029E ; 229E
	RET ; 00EE
LBL0720: LD I, LBL0A5A ; AA5A
	LDM V0 ; F065
	ADD V0, #01 ; 7001
	STM V0 ; F055
	RET ; 00EE
LBL072A: LD I, LBL0A5A ; AA5A
	LDM V0 ; F065
	STD V0 ; F033
	LDM V2 ; F265
	LD VE, #1B ; 6E1B
	LD VD, #31 ; 6D31
	LDH I, V0 ; F030
	DRAW VD, VE, 10 ; DDEA
	ADD VD, #0A ; 7D0A
	LDH I, V1 ; F130
	DRAW VD, VE, 10 ; DDEA
	ADD VD, #0A ; 7D0A
	LDH I, V2 ; F230
	DRAW VD, VE, 10 ; DDEA
	RET ; 00EE
LBL0748: LD V3, #00 ; 6300
	LD V4, #00 ; 6400
	LD V5, #7C ; 657C
	LD V6, #3E ; 663E
LBL0750: LD I, LBL0A5E ; AA5E
LBL0752: DRAW V3, V4, 3 ; D343
	DRAW V3, V6, 3 ; D363
	DRAW V5, V4, 3 ; D543
	DRAW V5, V6, 3 ; D563
	ADD V3, #04 ; 7304
	ADD V4, #02 ; 7402
	ADD V5, #FC ; 75FC
	ADD V6, #FE ; 76FE
	LD VD, #04 ; 6D04
	CALL LBL029E ; 229E
	SNE V3, #40 ; 4340
	RET ; 00EE
	SNE V3, #80 ; 4380
	RET ; 00EE
	JP LBL0752 ; 1752
LBL0770: LD V4, #00 ; 6400
	LD V5, #00 ; 6500
	LD V0, #70 ; 6070
	LD V1, #14 ; 6114
	LD I, LBL0A62 ; AA62
	DRAW V0, V1, 8 ; D018
	LD I, LBL0A82 ; AA82
	STM V5 ; F555
	RET ; 00EE
LBL0782: SNE V1, #00 ; 4100
	JP LBL07D0 ; 17D0
	SNE V1, #34 ; 4134
	JP LBL07D8 ; 17D8
	LD VD, #02 ; 6D02
	SE V3, VD ; 53D0
	JP LBL079E ; 179E
	SNE V1, #14 ; 4114
	JP LBL07AC ; 17AC
	SNE V1, #08 ; 4108
	JP LBL07BE ; 17BE
	SNE V1, #20 ; 4120
	JP LBL07BE ; 17BE
	RET ; 00EE
LBL079E: SNE V1, #20 ; 4120
	JP LBL07AC ; 17AC
	SNE V1, #14 ; 4114
	JP LBL07BE ; 17BE
	SNE V1, #2C ; 412C
	JP LBL07BE ; 17BE
	RET ; 00EE
LBL07AC: LD VD, #10 ; 6D10
	SUBN VD, V0 ; 8D07
	SNE VF, #00 ; 4F00
	JP LBL07E8 ; 17E8
	LD VD, #68 ; 6D68
	SUB VD, V0 ; 8D05
	SNE VF, #00 ; 4F00
	JP LBL07E8 ; 17E8
	RET ; 00EE
LBL07BE: LD VD, #29 ; 6D29
	SUBN VD, V0 ; 8D07
	SNE VF, #00 ; 4F00
	RET ; 00EE
	LD VD, #50 ; 6D50
	SUBN VD, V0 ; 8D07
	SNE VF, #00 ; 4F00
	JP LBL07E8 ; 17E8
	RET ; 00EE
LBL07D0: LD VD, #FE ; 6DFE
	SNE V3, VD ; 93D0
	CALL LBL04A0 ; 24A0
	RET ; 00EE
LBL07D8: LD VD, #02 ; 6D02
	SE V3, VD ; 53D0
	RET ; 00EE
	SNE V8, #00 ; 4800
	JP LBL07E8 ; 17E8
	SE V8, #00 ; 3800
	JP LBL07AC ; 17AC
	RET ; 00EE
LBL07E8: LD V3, #00 ; 6300
	RET ; 00EE
LBL07EC: SNE V2, #00 ; 4200
	RET ; 00EE
	LD VD, #04 ; 6D04
	SE V2, VD ; 52D0
	JP LBL0800 ; 1800
	SNE V0, #68 ; 4068
	JP LBL080A ; 180A
	SNE V0, #28 ; 4028
	JP LBL081C ; 181C
	RET ; 00EE
LBL0800: SNE V0, #10 ; 4010
	JP LBL080A ; 180A
	SNE V0, #50 ; 4050
	JP LBL081C ; 181C
	RET ; 00EE
LBL080A: LD VD, #11 ; 6D11
	SUBN VD, V1 ; 8D17
	SNE VF, #00 ; 4F00
	RET ; 00EE
	LD VD, #21 ; 6D21
	SUBN VD, V1 ; 8D17
	SNE VF, #00 ; 4F00
	JP LBL0848 ; 1848
	RET ; 00EE
LBL081C: LD VD, #1C ; 6D1C
	SUB VD, V1 ; 8D15
	SNE VF, #00 ; 4F00
	JP LBL0836 ; 1836
	LD VD, #05 ; 6D05
	SUBN VD, V1 ; 8D17
	SNE VF, #00 ; 4F00
	RET ; 00EE
	LD VD, #15 ; 6D15
	SUBN VD, V1 ; 8D17
	SNE VF, #00 ; 4F00
	JP LBL0848 ; 1848
	RET ; 00EE
LBL0836: LD VD, #1D ; 6D1D
	SUBN VD, V1 ; 8D17
	SNE VF, #00 ; 4F00
	RET ; 00EE
	LD VD, #2D ; 6D2D
	SUBN VD, V1 ; 8D17
	SNE VF, #00 ; 4F00
	JP LBL0848 ; 1848
	RET ; 00EE
LBL0848: LD V2, #00 ; 6200
	RET ; 00EE
LBL084C: CLS ; 00E0
	LD VD, #00 ; 6D00
	LD VE, #3C ; 6E3C
	LD I, LBL0AAC ; AAAC
	DRAW VD, VE, 4 ; DDE4
	LD VD, #08 ; 6D08
	DRAW VD, VE, 4 ; DDE4
	LD I, LBL0AA8 ; AAA8
	LD VD, #10 ; 6D10
	SNE V8, #00 ; 4800
	CALL LBL08A8 ; 28A8
	SE V8, #00 ; 3800
	CALL LBL08B2 ; 28B2
	LD I, LBL0AA8 ; AAA8
	LD VE, #1C ; 6E1C
	LD VD, #78 ; 6D78
	DRAW VD, VE, 4 ; DDE4
	LD VD, #00 ; 6D00
	DRAW VD, VE, 4 ; DDE4
	LD VD, #38 ; 6D38
	LD VE, #10 ; 6E10
	DRAW VD, VE, 4 ; DDE4
	LD VD, #40 ; 6D40
	DRAW VD, VE, 4 ; DDE4
	LD VE, #28 ; 6E28
	DRAW VD, VE, 4 ; DDE4
	LD VD, #38 ; 6D38
	DRAW VD, VE, 4 ; DDE4
	LD I, LBL0AA0 ; AAA0
	LD VD, #48 ; 6D48
	DRAW VD, VE, 4 ; DDE4
	LD VE, #10 ; 6E10
	DRAW VD, VE, 4 ; DDE4
	LD VD, #08 ; 6D08
	LD VE, #1C ; 6E1C
	DRAW VD, VE, 4 ; DDE4
	LD I, LBL0AA4 ; AAA4
	LD VD, #70 ; 6D70
	DRAW VD, VE, 4 ; DDE4
	LD VE, #28 ; 6E28
	LD VD, #30 ; 6D30
	DRAW VD, VE, 4 ; DDE4
	LD VE, #10 ; 6E10
	DRAW VD, VE, 4 ; DDE4
	CALL LBL08D2 ; 28D2
	RET ; 00EE
LBL08A8: DRAW VD, VE, 4 ; DDE4
	ADD VD, #08 ; 7D08
	SE VD, #80 ; 3D80
	JP LBL08A8 ; 18A8
	RET ; 00EE
LBL08B2: LD VD, #70 ; 6D70
	DRAW VD, VE, 4 ; DDE4
	LD VD, #78 ; 6D78
	DRAW VD, VE, 4 ; DDE4
	LD VD, #10 ; 6D10
	LD I, LBL0AB4 ; AAB4
	LD VE, #3B ; 6E3B
LBL08C0: DRAW VD, VE, 5 ; DDE5
	ADD VD, #08 ; 7D08
	SE VD, #70 ; 3D70
	JP LBL08C0 ; 18C0
	LD V0, #68 ; 6068
	LD V1, #F8 ; 61F8
	LD I, LBL0AC0 ; AAC0
	STM V1 ; F155
	RET ; 00EE
LBL08D2: SNE V9, #01 ; 4901
	RET ; 00EE
	LD VD, #01 ; 6D01
	LD VE, #3D ; 6E3D
	LD I, LBL0A5E ; AA5E
	DRAW VD, VE, 3 ; DDE3
	ADD VD, #04 ; 7D04
	SE V9, #02 ; 3902
	DRAW VD, VE, 3 ; DDE3
	ADD VD, #04 ; 7D04
	LD V6, #03 ; 6603
	SUB V6, V9 ; 8695
	SNE VF, #00 ; 4F00
	DRAW VD, VE, 3 ; DDE3
	RET ; 00EE
LBL08F0: LD I, LBL0AC6 ; AAC6
	LD VD, #24 ; 6D24
	LD VE, #18 ; 6E18
	DRAW VD, VE, 0 ; DDE0
	LD V0, #20 ; 6020
	ADD I, V0 ; F01E
	ADD VD, #10 ; 7D10
	DRAW VD, VE, 0 ; DDE0
	ADD I, V0 ; F01E
	ADD VD, #10 ; 7D10
	DRAW VD, VE, 0 ; DDE0
	ADD I, V0 ; F01E
	ADD VD, #10 ; 7D10
	DRAW VD, VE, 0 ; DDE0
LBL090C: LD V8, #00 ; 6800
	LD VB, #01 ; 6B01
	LD VA, #00 ; 6A00
	CALL LBL05F8 ; 25F8
	CALL LBL0770 ; 2770
	CALL LBL0496 ; 2496
	LD I, LBL0A82 ; AA82
	STM V5 ; F555
LBL091C: LD VD, #0A ; 6D0A
	CALL LBL029E ; 229E
	LD I, LBL0A82 ; AA82
	LDM V5 ; F565
	CALL LBL0940 ; 2940
	CALL LBL02D2 ; 22D2
	LD I, LBL0A82 ; AA82
	STM V5 ; F555
	LD I, LBL0A88 ; AA88
	LDM V5 ; F565
	CALL LBL0940 ; 2940
	CALL LBL0392 ; 2392
	LD I, LBL0A88 ; AA88
	STM V5 ; F555
	LD VD, #0A ; 6D0A
	SKP VD ; ED9E
	JP LBL091C ; 191C
	RET ; 00EE
LBL0940: RND VD, #0F ; CD0F
	SNE VD, #00 ; 4D00
	CALL LBL04A4 ; 24A4
	SNE V1, #02 ; 4102
	LD V3, #02 ; 6302
	SNE V1, #36 ; 4136
	LD V3, #FE ; 63FE
	RET ; 00EE
LBL0950: CALL LBL084C ; 284C
	CALL LBL0770 ; 2770
	LD I, LBL0AC2 ; AAC2
	LD VE, #0C ; 6E0C
	LD VD, #32 ; 6D32
	DRAW VD, VE, 4 ; DDE4
	ADD VD, #0C ; 7D0C
	DRAW VD, VE, 4 ; DDE4
	ADD VD, #0C ; 7D0C
	DRAW VD, VE, 4 ; DDE4
	LD VE, #24 ; 6E24
	LD VD, #32 ; 6D32
	DRAW VD, VE, 4 ; DDE4
	ADD VD, #0C ; 7D0C
	DRAW VD, VE, 4 ; DDE4
	ADD VD, #0C ; 7D0C
	DRAW VD, VE, 4 ; DDE4
	LD VE, #18 ; 6E18
	LD VD, #0A ; 6D0A
	DRAW VD, VE, 4 ; DDE4
	LD VE, #38 ; 6E38
	DRAW VD, VE, 4 ; DDE4
	LD VD, #72 ; 6D72
	DRAW VD, VE, 4 ; DDE4
	LD V6, #00 ; 6600
	LD V7, #00 ; 6700
LBL0984: ADD V7, #01 ; 7701
	SNE V7, #6A ; 476A
	JP LBL021E ; 121E
	LD VD, #01 ; 6D01
	LD ST, VD ; FD18
	LD VD, #03 ; 6D03
	CALL LBL029E ; 229E
	LD I, LBL0A82 ; AA82
	LDM V5 ; F565
	CALL LBL04A0 ; 24A0
	LD V2, #00 ; 6200
	LD VD, #0A ; 6D0A
	SKNP VD ; EDA1
	CALL LBL049C ; 249C
	LD VD, #03 ; 6D03
	SKNP VD ; EDA1
	CALL LBL0490 ; 2490
	LD VD, #0C ; 6D0C
	SKNP VD ; EDA1
	CALL LBL0496 ; 2496
	CALL LBL0782 ; 2782
	CALL LBL07EC ; 27EC
	LD VD, V0 ; 8D00
	LD VE, V1 ; 8E10
	ADD V0, V2 ; 8024
	ADD V1, V3 ; 8134
	LD I, LBL0A62 ; AA62
	ADD I, V5 ; F51E
	LD V5, #7F ; 657F
	AND V0, V5 ; 8052
	LD V5, V4 ; 8540
	DRAW VD, VE, 8 ; DDE8
	LD I, LBL0A62 ; AA62
	ADD I, V4 ; F41E
	DRAW V0, V1, 8 ; D018
	SNE V1, #38 ; 4138
	JP LBL0A38 ; 1A38
	LD I, LBL0A82 ; AA82
	STM V5 ; F555
	SE VF, #00 ; 3F00
	CALL LBL09DC ; 29DC
	SNE V6, #09 ; 4609
	JP LBL0A48 ; 1A48
	JP LBL0984 ; 1984
LBL09DC: LD VE, #34 ; 6E34
	SNE V1, VE ; 91E0
	JP LBL09F6 ; 19F6
	LD VE, #14 ; 6E14
	SNE V1, VE ; 91E0
	JP LBL0A04 ; 1A04
	LD VE, #08 ; 6E08
	SNE V1, VE ; 91E0
	JP LBL0A0C ; 1A0C
	LD VE, #20 ; 6E20
	SNE V1, VE ; 91E0
	JP LBL0A0C ; 1A0C
	RET ; 00EE
LBL09F6: LD VD, #70 ; 6D70
	SNE V0, VD ; 90D0
	JP LBL0A20 ; 1A20
	LD VD, #08 ; 6D08
	SNE V0, VD ; 90D0
	JP LBL0A20 ; 1A20
	RET ; 00EE
LBL0A04: LD VD, #08 ; 6D08
	SNE V0, VD ; 90D0
	JP LBL0A20 ; 1A20
	RET ; 00EE
LBL0A0C: LD VD, #30 ; 6D30
	SNE V0, VD ; 90D0
	JP LBL0A20 ; 1A20
	ADD VD, #0C ; 7D0C
	SNE V0, VD ; 90D0
	JP LBL0A20 ; 1A20
	ADD VD, #0C ; 7D0C
	SNE V0, VD ; 90D0
	JP LBL0A20 ; 1A20
	RET ; 00EE
LBL0A20: ADD VD, #02 ; 7D02
	ADD VE, #04 ; 7E04
	LD I, LBL0AC2 ; AAC2
	DRAW VD, VE, 4 ; DDE4
	CALL LBL0702 ; 2702
	CALL LBL0702 ; 2702
	ADD V6, #01 ; 7601
	LD I, LBL0A5A ; AA5A
	LDM V0 ; F065
	ADD V0, #01 ; 7001
	STM V0 ; F055
	RET ; 00EE
LBL0A38: LD VD, #08 ; 6D08
	LD ST, VD ; FD18
	LD VD, #14 ; 6D14
	CALL LBL029E ; 229E
	ADD V9, #FF ; 79FF
	SNE V9, #00 ; 4900
	JP LBL06DA ; 16DA
	JP LBL021E ; 121E
LBL0A48: LD I, LBL0A5A ; AA5A
	LDM V0 ; F065
	ADD V0, #08 ; 7008
	STM V0 ; F055
	ADD V9, #01 ; 7901
	CALL LBL0716 ; 2716
	CALL LBL070C ; 270C
	CALL LBL0716 ; 2716
	JP LBL021E ; 121E
LBL0A5A: DB #00
	DB #00
	DB #00
	DB #00
LBL0A5E: SNE V0, #E0 ; 40E0
	SNE V0, #00 ; 4000
LBL0A62: LD V6, #6F ; 666F
	SNE VC, #FF ; 4CFF
	LD VC, #DC ; 6CDC
	DB #EC
	ADD V8, #66 ; 7866
	DB #F6
	SE V2, #FF ; 32FF
	SE V6, #3B ; 363B
	SE V7, #1E ; 371E
LBL0A72: LD VE, #6F ; 6E6F
	SNE VC, #FF ; 4CFF
	LD VC, #BE ; 6CBE
	DB #9E
	ADD VC, #76 ; 7C76
	DB #F6
	SE V2, #FF ; 32FF
	SE V6, #7D ; 367D
	ADD V9, #3E ; 793E
LBL0A82: DB #00
	DB #00
	DB #00
	DB #00
	DB #00
	DB #00
LBL0A88: DB #00
	DB #00
	DB #00
	DB #00
	DB #00
	DB #00
LBL0A8E: DB #00
	DB #00
	DB #00
	DB #00
	DB #00
	DB #00
LBL0A94: DB #00
	DB #00
	DB #00
	DB #00
	DB #00
	DB #00
LBL0A9A: DB #00
	DB #00
	DB #00
	DB #00
	DB #00
	HIGH ; 00FF
	JP V0, LBL0AE8 ; BAE8
	DB #80
LBL0AA4: DB #FF
	LD VD, #1B ; 6D1B
	DB #02
LBL0AA8: DB #FF
	DB #EE
	JP V0, LBL0BB6 ; BBB6
LBL0AAC: DB #FF
	DB #FF
	DB #FF
	DB #FF
LBL0AB0: DB #00
	DB #00
	DB #00
	DB #00
LBL0AB4: DB #06
	JP LBL0C28 ; 1C28
	SNE VC, #FE ; 4CFE
	DB #00
LBL0ABA: LD V6, #24 ; 6624
	SE VC, #6E ; 3C6E
	DB #00
	DB #00
LBL0AC0: DB #00
	DB #00
LBL0AC2: LD V0, #B0 ; 60B0
	DB #F0
	LD V0, #00 ; 6000
	RND V0, #00 ; C000
	RND V0, #00 ; C000
	RND V0, #00 ; C000
	RND V0, #00 ; C000
	RND V0, #00 ; C000
	RND V0, #00 ; C000
	RND V3, #00 ; C300
	RND V7, #00 ; C700
	RND VC, #00 ; CC00
	RND VC, #C0 ; CCC0
	RND VC, #C0 ; CCC0
	RND VC, #C0 ; CCC0
	RND VC, #C0 ; CCC0
	RND VC, #7F ; CC7F
	DB #87
	SE VF, #03 ; 3F03
	DB #00
	DB #00
LBL0AE8: DB #00
	DB #00
	DB #00
	DB #00
	DB #00
	DB #00
	DB #00
	DB #00
	DB #00
	DB #00
	DB #F0
	RND V0, #F8 ; C0F8
	RND V0, #0C ; C00C
	RND V0, #0C ; C00C
	RND V0, #0C ; C00C
	RND V0, #0C ; C00C
	RND V0, #0C ; C00C
	RND V0, #0C ; C00C
	RND V0, #F8 ; C0F8
	ADD VF, #F0 ; 7FF0
	SE VF, #00 ; 3F00
	DB #00
	DB #00
	DB #00
	DB #00
	DB #00
	DB #00
	DB #00
	DB #00
	DB #00
	DB #00
	SCD #03 ; 00C3
	DB #FC
	RND V7, #FC ; C7FC
	RND VC, #00 ; CC00
	RND VC, #00 ; CC00
	RND V7, #F0 ; C7F0
	RND V3, #F8 ; C3F8
	RND V0, #0C ; C00C
	RND V0, #0C ; C00C
	RND VF, #F8 ; CFF8
	RND VF, #F0 ; CFF0
	DB #00
	DB #00
	DB #00
	DB #00
	SE V0, #00 ; 3000
	SE V0, #00 ; 3000
	SE V0, #00 ; 3000
	SE V0, #00 ; 3000
	DB #FC
	SCL ; 00FC
	DB #00
	SE V0, #00 ; 3000
	SE V0, #00 ; 3000
	SE V0, #00 ; 3000
	SE V0, #00 ; 3000
	SE V3, #00 ; 3300
	SE V3, #00 ; 3300
	JP LBL0E00 ; 1E00
	DB #0C
	DB #00