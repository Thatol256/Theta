# Theta

I have always wanted to create an SNES game in order to test my knowledge of the hardware. However, there were a couple of obsticals in my way:
1. Programming in raw Assembly is slow and painful.
2. Programming in other languages usually require the use of libraries, and with my luck, I am always unable to get it to work.

So, here is a project that solves both problems.

Theta is a programming language that will easily allow you to generate Assembly code for any Assembly language, and does not require any dependencies, libraries, or installations other than the Python programming language. The language works by converting Theta code into Python code. After that, an Assembly module is introduced, and overrides Python's functionality to generate Assembly code rather than actually executing Python code. An Assembly module is a script made specifically for a specific Assembly language, and the Pre-Processor script simplifies code as much as possible, so the creation of an Assembly module requires minimal effort.

## Current Progress
- The Pre-processor is, to my knowledge, mostly complete, although there is definitely minimal error checking.
- The framework of the provided Assembly module (asm_65816.py) is mostly complete, however has minimal Assembly generation.

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
	
	u16<0x2100> INIDISP
	u16<0x4200> NMITIMEN
	u16<0x2105> BGMODE
	u16<0x4210> RDNMI
	
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

	INIDISP = ushort(0x2100)
	NMITIMEN = ushort(0x4200)
	BGMODE = ushort(0x2105)
	RDNMI = ushort(0x4210)
	
	main = general.Label("main")
	ID_1FA8AF621A4E41D = AddressingMode("PC.C")
	ID_1FA8AF621A4E41D = AddressingMode("False")
	asm("xce; rep #$10; sep #$20;")
	X = AddressingMode("0x33")
	
	ID_1FA8AF621A4E17F = general.Label("ID_1FA8AF621A4E17F")
	scopeStart("while", "PC.N == False", "ID_1FA8AF621A4E17F", "ID_1FA8AF621A4E199")
	ID_1FA8AF621A4E42D = AddressingMode("INIDISP + X")
	ID_1FA8AF621A4E42D = AddressingMode("0")
	ID_1FA8AF621A4E435 = AddressingMode("NMITIMEN + X")
	ID_1FA8AF621A4E435 = AddressingMode("0")
	X -= AddressingMode("1")
	scopeEnd()
	ID_1FA8AF621A4E199 = general.Label("ID_1FA8AF621A4E199")
	
	INIDISP = AddressingMode("0x8F")
	NMITIMEN = AddressingMode("0x81")
	BGMODE = AddressingMode("0x13")
	
	loop = general.Label("loop")
	wait()
	goto(loop)
	
	ID_1FA8AF621A4E1B5 = general.Label("ID_1FA8AF621A4E1B5")
	scopeStart(["void", "nmi"], [], "ID_1FA8AF621A4E1B5", "ID_1FA8AF621A4E1B9")
	asm("rep #$10; sep #$20;")
	DP.push(); A.push(); X.push(); Y.push()
	A = AddressingMode("RDNMI")
	Y.pull(); X.pull(); A.pull(); DP.pull()
	funcReturn()
	scopeEnd()
	ID_1FA8AF621A4E1B9 = general.Label("ID_1FA8AF621A4E1B9")

### After the Assembly Module (Assembly code):

	TODO
