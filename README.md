# Theta

I have always wanted to create an SNES game in order to test my knowledge of the hardware. However, there were a couple of obsticals in my way:
1. Programming in raw Assembly is slow and painful.
2. Programming in other languages usually require the use of libraries, and with my luck, I am always unable to get it to work.

So, here is a project that solves both problems.

Theta is a programming language that will easily allow you to generate Assembly code for any Assembly language, and does not require any dependencies, libraries, or installations other than the Python programming language. The language works by converting Theta code into Python code. After that, an Assembly module is introduced, and overrides Python's functionality to generate Assembly code rather than actually executing Python code. An Assembly module is a script made specifically for a specific Assembly language, and the Pre-Processor script simplifies code as much as possible, so the creation of an Assembly module requires minimal effort.

## Current Progress
- The Pre-processor is, at the moment, complete, although there is definitely minimal error checking.
- The provided Assembly module (asm_65816.py) supports most instructions besides jump/branch/compare instructions, and also supports addressing modes.
- Variable assignment has been complete, and supports both addressing modes and custom-sized unsigned integers, though there has not been a lot of error checking yet.
- At the moment, the script does not produce any output files, and the only way to run the script is to have a file named "test.tha" in the same directory.

## WARNINGS:
- These scripts can easily be modified to become malware, so only run versions of this project or Assembly modules you trust!
- This project does not produce hardware-specific information like headers, so don't expect to be able to immediately compile what you generate!
- This project is made with glue and stapples; Don't be suprised if something doesn't work!
- The programming language expects very specific syntax; Just breathing wrong can throw it off!
- The output Assembly code is not optimized; Don't expect it to run fast!

## How to use:
- Download the repository
- Download an Assembly module script that corresponds to the Assembly language you want to program in. This repository already has one built-in for 65816 Assembly.
- Create some code you want to convert.
- Open the "main.py" script and put in the input and output files, or you can run the script on the command line with "main.py -o OUTPUT_FILE"

## Example code:

### Before the pre-processor (Theta code):

	use asm_65816
	
	u8<0x2100> INIDISP
	u8<0x4200> NMITIMEN
	u8<0x2105> BGMODE
	u8<0x4210> RDNMI
	
	main:
	PC.C = False
	asm("xce; rep #$10; sep #$20;")
	X = 0x33
	
	while (PC.N == False) {
		INIDISP + X = 0
		NMITIMEN + X = 0
		X -= 1
	}
	
	INIDISP = 0x8F
	NMITIMEN = 0x81
	BGMODE = 0x13
	
	u8<0x2107> BG1SC
	u8<0x210B> BG12NBA
	u8<0x2101> OBJSEL
	u8<0x2115> VMAINC
	u8<0x2116> VMADDL
	u8<0x2117> VMADDH
	
	BG1SC = 0x50
	BG12NBA = 0
	OBJSEL = 3
	
	Y = 0
	VMAINC = 0
	VMADDL = 0
	VMADDH = 0
	X = 0
	
	u8<0x1234> VRAMDATA
	u8<0x2119> VMDATAHW
	u8<0x2118> VMDATALW
	
	while (Y != 4) {
		while (X != 0) {
			VRAMDATA + X = A
			VMDATAHW = A
			X += 1
			A = VRAMDATA + X
			VMDATALW = A
			X += 1
		}
		Y += 1
	}
	
	u8<0x212C> TM
	u8<0x212D> TS
	
	TM = 0x10
	TS = 0x10
	INIDISP = 0x0F
	
	loop:
	wait()
	goto(loop)
	
	void nmi () {
		asm("rep #$10; sep #$20;")
		DP.push(); A.push(); X.push(); Y.push()
		A = RDNMI
		Y.pull(); X.pull(); A.pull(); DP.pull()
		return
	}

### After the pre-processor (Python code):

	INIDISP = ubyte("INIDISP", 0x2100)
	general.VARIABLES.append(INIDISP)
	NMITIMEN = ubyte("NMITIMEN", 0x4200)
	general.VARIABLES.append(NMITIMEN)
	BGMODE = ubyte("BGMODE", 0x2105)
	general.VARIABLES.append(BGMODE)
	RDNMI = ubyte("RDNMI", 0x4210)
	general.VARIABLES.append(RDNMI)
	
	main = general.Label("main")
	general.LABELS.append(main)
	PC.C = False
	asm("xce; rep #$10; sep #$20;")
	X.value = 0x33
	ID_1FA8DE97C6E1189 = general.Label("ID_1FA8DE97C6E1189")
	general.LABELS.append(ID_1FA8DE97C6E1189)
	scopeStart("while", "PC.N == False", "ID_1FA8DE97C6E1189", "ID_1FA8DE97C6E11A3")
	
	INIDISP.assign(0, "=", AddressingMode("INIDISP + X"))
	NMITIMEN.assign(0, "=", AddressingMode("NMITIMEN + X"))
	X -= 1
	scopeEnd()
	ID_1FA8DE97C6E11A3 = general.Label("ID_1FA8DE97C6E11A3")
	general.LABELS.append(ID_1FA8DE97C6E11A3)
	
	INIDISP.assign(0x8F, "=", AddressingMode("INIDISP"))
	NMITIMEN.assign(0x81, "=", AddressingMode("NMITIMEN"))
	BGMODE.assign(0x13, "=", AddressingMode("BGMODE"))
	
	BG1SC = ubyte("BG1SC", 0x2107)
	general.VARIABLES.append(BG1SC)
	BG12NBA = ubyte("BG12NBA", 0x210B)
	general.VARIABLES.append(BG12NBA)
	OBJSEL = ubyte("OBJSEL", 0x2101)
	general.VARIABLES.append(OBJSEL)
	VMAINC = ubyte("VMAINC", 0x2115)
	general.VARIABLES.append(VMAINC)
	VMADDL = ubyte("VMADDL", 0x2116)
	general.VARIABLES.append(VMADDL)
	VMADDH = ubyte("VMADDH", 0x2117)
	general.VARIABLES.append(VMADDH)
	
	BG1SC.assign(0x50, "=", AddressingMode("BG1SC"))
	BG12NBA.assign(0, "=", AddressingMode("BG12NBA"))
	OBJSEL.assign(3, "=", AddressingMode("OBJSEL"))
	
	Y.value = 0
	VMAINC.assign(0, "=", AddressingMode("VMAINC"))
	VMADDL.assign(0, "=", AddressingMode("VMADDL"))
	VMADDH.assign(0, "=", AddressingMode("VMADDH"))
	X.value = 0
	
	VRAMDATA = ubyte("VRAMDATA", 0x1234)
	general.VARIABLES.append(VRAMDATA)
	VMDATAHW = ubyte("VMDATAHW", 0x2119)
	general.VARIABLES.append(VMDATAHW)
	VMDATALW = ubyte("VMDATALW", 0x2118)
	general.VARIABLES.append(VMDATALW)
	ID_1FA8DE97C6E11CB = general.Label("ID_1FA8DE97C6E11CB")
	general.LABELS.append(ID_1FA8DE97C6E11CB)
	scopeStart("while", "Y != 4", "ID_1FA8DE97C6E11CB", "ID_1FA8DE97C6E11CE")
	ID_1FA8DE97C6E11E9 = general.Label("ID_1FA8DE97C6E11E9")
	general.LABELS.append(ID_1FA8DE97C6E11E9)
	scopeStart("while", "X != 0", "ID_1FA8DE97C6E11E9", "ID_1FA8DE97C6E11EC")
	
	VRAMDATA.assign(A, "=", AddressingMode("VRAMDATA + X"))
	VMDATAHW.assign(A, "=", AddressingMode("VMDATAHW"))
	X += 1
	A.value = AddressingMode("VRAMDATA + X")
	VMDATALW.assign(A, "=", AddressingMode("VMDATALW"))
	X += 1
	scopeEnd()
	ID_1FA8DE97C6E11EC = general.Label("ID_1FA8DE97C6E11EC")
	general.LABELS.append(ID_1FA8DE97C6E11EC)
	Y += 1
	scopeEnd()
	ID_1FA8DE97C6E11CE = general.Label("ID_1FA8DE97C6E11CE")
	general.LABELS.append(ID_1FA8DE97C6E11CE)
	
	TM = ubyte("TM", 0x212C)
	general.VARIABLES.append(TM)
	TS = ubyte("TS", 0x212D)
	general.VARIABLES.append(TS)
	
	TM.assign(0x10, "=", AddressingMode("TM"))
	TS.assign(0x10, "=", AddressingMode("TS"))
	INIDISP.assign(0x0F, "=", AddressingMode("INIDISP"))
	
	loop = general.Label("loop")
	general.LABELS.append(loop)
	wait()
	goto(loop)
	ID_1FA8DE97C6E1208 = general.Label("ID_1FA8DE97C6E1208")
	general.LABELS.append(ID_1FA8DE97C6E1208)
	scopeStart(["void", "nmi"], [], "ID_1FA8DE97C6E1208", "ID_1FA8DE97C6E120A")
	
	asm("rep #$10; sep #$20;")
	DP.push(); A.push(); X.push(); Y.push()
	A.value = RDNMI
	Y.pull(); X.pull(); A.pull(); DP.pull()
	funcReturn()
	scopeEnd()
	ID_1FA8DE97C6E120A = general.Label("ID_1FA8DE97C6E120A")
	general.LABELS.append(ID_1FA8DE97C6E120A)

### After the Assembly Module (Assembly code) (NOT COMPLETE):

	main:
		xce
		rep #$10
		sep #$20
	
	ID_1FA8CB4D41885B1:
		dex
	
	ID_1FA8CB4D41885CE:
	loop:
		wai
	
	ID_1FA8CB4D41885EC:
		rep #$10
		sep #$20
		pha
		phx
		phy
		lda $4210
		ply
		plx
		pla
	ID_1FA8CB4D41885EF:
