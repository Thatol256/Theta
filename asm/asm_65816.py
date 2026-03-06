import general

def asm(op):
	if isinstance(op, list): op = ";".join(op)
	for o in op.split(";"):
		if o != "": general.asm.append(o.strip())
def wait(): asm("wai;")
def nop(): asm("nop;")

DATATYPES = ["ubyte", "ushort", "uint", "sbyte", "sshort", "sint", "vector", "pointer", "array"]
REGISTERS = ["A", "X", "Y", "PC"]
ALIASES = {"u8": "ubyte", "u16": "ushort", "u32": "uint", "i8": "sbyte", "i16": "sshort", "i32": "sint"}

RE_UINT = r"0x[0-9A-Fa-f]+|%[01]+|\d+"
RE_INT = fr"-?(?:{RE_UINT})"
RE_SYMBOL = r"\w[\w\d]*"

MODE_IMMEDIATE = 0
MODE_RELATIVE = 1
MODE_DIRECT = 2
MODE_DIRECT_INDIRECT = 3
MODE_DIRECT_INDIRECT_LONG = 4
MODE_DIRECT_X = 5
MODE_DIRECT_Y = 6
MODE_DIRECT_INDIRECT_X = 7
MODE_DIRECT_INDIRECT_Y = 8
MODE_DIRECT_INDIRECT_LONG_Y = 9
MODE_ABSOLUTE = 10
MODE_ABSOLUTE_X = 11
MODE_ABSOLUTE_Y = 12
MODE_ABSOLUTE_LONG = 13
MODE_ABSOLUTE_LONG_X = 14
MODE_ABSOLUTE_INDIRECT = 15
MODE_ABSOLUTE_INDIRECT_LONG = 16
MODE_ABSOLUTE_INDIRECT_X = 17
MODE_STACK_RELATIVE = 18
MODE_STACK_RELATIVE_INDIRECT_Y = 19

# "#" means this is an address, "&" means the value at that address
ADDRESSING_MODES = [
	{ "name": "immediate",                 "match": f"({RE_INT})",                      "swap": "1",       "maximumSize": 2 },
	{ "name": "relative",                  "match": fr"PC([\+\-]{RE_UINT})",            "swap": "1",       "maximumSize": 1 },
	{ "name": "direct",                    "match": f"#({RE_UINT})",                    "swap": "1",       "maximumSize": 1 },
	{ "name": "direct indirect",           "match": f"&2:#({RE_UINT})",                 "swap": "(1)",     "maximumSize": 1 },
	{ "name": "direct indirect long",      "match": f"&3:#({RE_UINT})",                 "swap": "[1]",     "maximumSize": 1 },
	{ "name": "direct x",                  "match": fr"#({RE_UINT})\+X",                "swap": "1,x",     "maximumSize": 1 },
	{ "name": "direct y",                  "match": fr"#({RE_UINT})\+Y",                "swap": "1,y",     "maximumSize": 1 },
	{ "name": "direct indirect x",         "match": fr"&2:\(#({RE_UINT})\+X\)",         "swap": "(1,x)",   "maximumSize": 1 },
	{ "name": "direct indirect y",         "match": fr"&2:\(#({RE_UINT})\)\+Y",         "swap": "(1),y",   "maximumSize": 1 },
	{ "name": "direct indirect long y",    "match": fr"&3:\(#({RE_UINT})\)\+Y",         "swap": "[1],y",   "maximumSize": 1 },
	{ "name": "absolute",                  "match": f"#({RE_UINT})",                    "swap": "1",       "maximumSize": 2 },
	{ "name": "absolute x",                "match": fr"#({RE_UINT})\+X",                "swap": "1,x",     "maximumSize": 2 },
	{ "name": "absolute y",                "match": fr"#({RE_UINT})\+Y",                "swap": "1,y",     "maximumSize": 2 },
	{ "name": "absolute long",             "match": f"#({RE_UINT})",                    "swap": "1",       "maximumSize": 3 },
	{ "name": "absolute long x",           "match": fr"#({RE_UINT})\+X",                "swap": "1,x",     "maximumSize": 3 },
	{ "name": "absolute indirect",         "match": f"&2:#({RE_UINT})",                 "swap": "(1)",     "maximumSize": 2 },
	{ "name": "absolute indirect long",    "match": f"&3:#({RE_UINT})",                 "swap": "[1]",     "maximumSize": 2 },
	{ "name": "absolute indirect x",       "match": fr"&2:\(#({RE_UINT})\+X\)",         "swap": "(1,x)",   "maximumSize": 2 },
	{ "name": "stack relative",            "match": fr"([\+\-]{RE_UINT})\+S",           "swap": "1,s",     "maximumSize": 1 },
	{ "name": "stack relative indirect y", "match": fr"&2:\(([\+\-]{RE_UINT})\+S\)\+Y", "swap": "(1,s),y", "maximumSize": 1 }
]

# also normalizes arg to hex
def identifyMode(txt):
	for i, a in enumerate(ADDRESSING_MODES):
		mat = re.search(f"^{a["match"]}$", txt)
		if mat == None: continue
		arg = mat.group(1)
		#if arg in REGISTERS: continue
		if re.search(RE_INT, arg.replace("+", "")) != None:
			arg = arg.replace("+", "")
			negative = "-" in arg
			if negative: arg = arg.replace("-", "")
			if "%" in arg: arg = f"${hex(int(arg[1:],2))[2:]}"
			if arg.isdigit(): arg = f"${hex(int(arg))[2:]}"
			if "0x" in arg: arg = f"${arg[2:]}"
			if negative: arg = f"-{arg}"
			iVal = int(arg.replace("$","").replace("-",""),16)
			bound = 256**a["maximumSize"]-1
			if not (iVal>=-bound and iVal<=bound): continue
		return i, arg
	return None, None
def modeSyntax(md, arg): return ADDRESSING_MODES[md]["swap"].replace("1", arg)

# *VAR -> 0x1234, &PTR -> &2:#0x1234, etc.
def resolveMode(txt):
	txt = txt.replace(" ", "")
	varNames = [x.name for x in general.VARIABLES]
	var = None
	for i, v in enumerate(varNames):
		if v in txt: var = general.VARIABLES[i]
	if var == None: return txt
	addr = f"0x{hex(var.address)[2:]}"
	txt = txt.replace(f"{var.name}", "#"+addr)
	if "*#" in txt: txt = txt.replace(f"*#", "")
	if "&" in txt:
		isPointer = True
		try: var.reference.width
		except: isPointer = False
		if isPointer: txt = txt.replace("&", f"&{var.reference.width}:")
		else: txt = txt.replace("&", f"&{var.width}:")
	return txt

'''
Address mode: None, None; From PC.C => PC.C
Address mode: None, None; From False => False
Address mode: Immediate, $33; From 0x33 => 0x33
Address mode: Absolute x, $2100; From INIDISP + X => #0x2100+X
Address mode: Immediate, $0; From 0 => 0
Address mode: Absolute x, $4200; From NMITIMEN + X => #0x4200+X
Address mode: Immediate, $0; From 0 => 0
Address mode: Immediate, $1; From 1 => 1
Address mode: Immediate, $8F; From 0x8F => 0x8F
Address mode: Immediate, $81; From 0x81 => 0x81
Address mode: Immediate, $13; From 0x13 => 0x13
Address mode: Absolute, $4210; From RDNMI => #0x4210

VAR -> #VAR.address
*VAR -> VAR.address
&(*VAR + X) -> &VAR.width:(VAR.address + X)
*PTR -> PTR.address
PTR -> #PTR.address
&PTR -> &PTR.reference.width:#PTR.address
&(*PTR + X) -> &PTR.reference.width:(PTR.address + X)

INSTRUCTIONS LEFT:
ASL dp 		Arithmetic Shift Left 	06 	Direct Page 	N-----ZC 	2 	5[2][4]
ASL A 		Arithmetic Shift Left 	0A 	Accumulator 	N-----ZC 	1 	2
ASL addr 		Arithmetic Shift Left 	0E 	Absolute 	N-----ZC 	3 	6[4]
ASL dp,X 		Arithmetic Shift Left 	16 	DP Indexed,X 	N-----ZC 	2 	6[2][4]
ASL addr,X 		Arithmetic Shift Left 	1E 	Absolute Indexed,X 	N-----ZC 	3 	7[4]
BCC nearlabel 	BLT 	Branch if Carry Clear 	90 	Program Counter Relative 		2 	2[5][6]
BCS nearlabel 	BGE 	Branch if Carry Set 	B0 	Program Counter Relative 		2 	2[5][6]
BEQ nearlabel 		Branch if Equal 	F0 	Program Counter Relative 		2 	2[5][6]
BIT dp 		Test Bits 	24 	Direct Page 	NV----Z- 	2 	3[1][2]
BIT addr 		Test Bits 	2C 	Absolute 	NV----Z- 	3 	4[1]
BIT dp,X 		Test Bits 	34 	DP Indexed,X 	NV----Z- 	2 	4[1][2]
BIT addr,X 		Test Bits 	3C 	Absolute Indexed,X 	NV----Z- 	3 	4[1][3]
BIT #const 		Test Bits 	89 	Immediate 	------Z- 	2[12] 	2[1]
BMI nearlabel 		Branch if Minus 	30 	Program Counter Relative 		2 	2[5][6]
BNE nearlabel 		Branch if Not Equal 	D0 	Program Counter Relative 		2 	2[5][6]
BPL nearlabel 		Branch if Plus 	10 	Program Counter Relative 		2 	2[5][6]
BRA nearlabel 		Branch Always 	80 	Program Counter Relative 		2 	3[6]
BRK 		Break 	00 	Stack/Interrupt 	----DI-- 	2[13] 	7[7]
BRL label 		Branch Long Always 	82 	Program Counter Relative Long 		3 	4
BVC nearlabel 		Branch if Overflow Clear 	50 	Program Counter Relative 		2 	2[5][6]
BVS nearlabel 		Branch if Overflow Set 	70 	Program Counter Relative 		2 	2[5][6]
CMP (dp,X) 		Compare Accumulator with Memory 	C1 	DP Indexed Indirect,X 	N-----ZC 	2 	6[1][2]
CMP sr,S 		Compare Accumulator with Memory 	C3 	Stack Relative 	N-----ZC 	2 	4[1]
CMP dp 		Compare Accumulator with Memory 	C5 	Direct Page 	N-----ZC 	2 	3[1][2]
CMP [dp] 		Compare Accumulator with Memory 	C7 	DP Indirect Long 	N-----ZC 	2 	6[1][2]
CMP #const 		Compare Accumulator with Memory 	C9 	Immediate 	N-----ZC 	2[12] 	2[1]
CMP addr 		Compare Accumulator with Memory 	CD 	Absolute 	N-----ZC 	3 	4[1]
CMP long 		Compare Accumulator with Memory 	CF 	Absolute Long 	N-----ZC 	4 	5[1]
CMP (dp),Y 		Compare Accumulator with Memory 	D1 	DP Indirect Indexed, Y 	N-----ZC 	2 	5[1][2][3]
CMP (dp) 		Compare Accumulator with Memory 	D2 	DP Indirect 	N-----ZC 	2 	5[1][2]
CMP (sr,S),Y 		Compare Accumulator with Memory 	D3 	SR Indirect Indexed,Y 	N-----ZC 	2 	7[1]
CMP dp,X 		Compare Accumulator with Memory 	D5 	DP Indexed,X 	N-----ZC 	2 	4[1][2]
CMP [dp],Y 		Compare Accumulator with Memory 	D7 	DP Indirect Long Indexed, Y 	N-----ZC 	2 	6[1][2]
CMP addr,Y 		Compare Accumulator with Memory 	D9 	Absolute Indexed,Y 	N-----ZC 	3 	4[1][3]
CMP addr,X 		Compare Accumulator with Memory 	DD 	Absolute Indexed,X 	N-----ZC 	3 	4[1][3]
CMP long,X 		Compare Accumulator with Memory 	DF 	Absolute Long Indexed,X 	N-----ZC 	4 	5[1]
COP #const 		Co-Processor 	02 	Stack/Interrupt 	----DI-- 	2[13] 	7[7]
CPX #const 		Compare Index Register X with Memory 	E0 	Immediate 	N-----ZC 	2[14] 	2[8]
CPX dp 		Compare Index Register X with Memory 	E4 	Direct Page 	N-----ZC 	2 	3[2][8]
CPX addr 		Compare Index Register X with Memory 	EC 	Absolute 	N-----ZC 	3 	4[8]
CPY #const 		Compare Index Register Y with Memory 	C0 	Immediate 	N-----ZC 	2[14] 	2[8]
CPY dp 		Compare Index Register Y with Memory 	C4 	Direct Page 	N-----ZC 	2 	3[2][8]
CPY addr 		Compare Index Register Y with Memory 	CC 	Absolute 	N-----ZC 	3 	4[8]
DEC A 	DEA 	Decrement 	3A 	Accumulator 	N-----Z- 	1 	2
DEC dp 		Decrement 	C6 	Direct Page 	N-----Z- 	2 	5[2][4]
DEC addr 		Decrement 	CE 	Absolute 	N-----Z- 	3 	6[4]
DEC dp,X 		Decrement 	D6 	DP Indexed,X 	N-----Z- 	2 	6[2][4]
DEC addr,X 		Decrement 	DE 	Absolute Indexed,X 	N-----Z- 	3 	7[4]
INC A 	INA 	Increment 	1A 	Accumulator 	N-----Z- 	1 	2
INC dp 		Increment 	E6 	Direct Page 	N-----Z- 	2 	5[2][4]
INC addr 		Increment 	EE 	Absolute 	N-----Z- 	3 	6[4]
INC dp,X 		Increment 	F6 	DP Indexed,X 	N-----Z- 	2 	6[2][4]
INC addr,X 		Increment 	FE 	Absolute Indexed,X 	N-----Z- 	3 	7[4]
JMP addr 		Jump 	4C 	Absolute 		3 	3
JMP long 	JML 	Jump 	5C 	Absolute Long 		4 	4
JMP (addr) 		Jump 	6C 	Absolute Indirect 		3 	5
JMP (addr,X) 		Jump 	7C 	Absolute Indexed Indirect 		3 	6
JMP [addr] 	JML 	Jump 	DC 	Absolute Indirect Long 		3 	6
JSR addr 		Jump to Subroutine 	20 	Absolute 		3 	6
JSR long 	JSL 	Jump to Subroutine 	22 	Absolute Long 		4 	8
JSR (addr,X)) 		Jump to Subroutine 	FC 	Absolute Indexed Indirect 		3 	8
LDX #const 		Load Index Register X from Memory 	A2 	Immediate 	N-----Z- 	2[14] 	2[8]
LDX dp 		Load Index Register X from Memory 	A6 	Direct Page 	N-----Z- 	2 	3[2][8]
LDX addr 		Load Index Register X from Memory 	AE 	Absolute 	N-----Z- 	3 	4[8]
LDX dp,Y 		Load Index Register X from Memory 	B6 	DP Indexed,Y 	N-----Z- 	2 	4[2][8]
LDX addr,Y 		Load Index Register X from Memory 	BE 	Absolute Indexed,Y 	N-----Z- 	3 	4[3][8]
LDY #const 		Load Index Register Y from Memory 	A0 	Immediate 	N-----Z- 	2[14] 	2[8]
LDY dp 		Load Index Register Y from Memory 	A4 	Direct Page 	N-----Z- 	2 	3[2][8]
LDY addr 		Load Index Register Y from Memory 	AC 	Absolute 	N-----Z- 	3 	4[8]
LDY dp,X 		Load Index Register Y from Memory 	B4 	DP Indexed,X 	N-----Z- 	2 	4[2][8]
LDY addr,X 		Load Index Register Y from Memory 	BC 	Absolute Indexed,X 	N-----Z- 	3 	4[3][8]
LSR dp 		Logical Shift Memory or Accumulator Right 	46 	Direct Page 	N-----ZC 	2 	5[2][4]
LSR A 		Logical Shift Memory or Accumulator Right 	4A 	Accumulator 	N-----ZC 	1 	2
LSR addr 		Logical Shift Memory or Accumulator Right 	4E 	Absolute 	N-----ZC 	3 	6[4]
LSR dp,X 		Logical Shift Memory or Accumulator Right 	56 	DP Indexed,X 	N-----ZC 	2 	6[2][4]
LSR addr,X 		Logical Shift Memory or Accumulator Right 	5E 	Absolute Indexed,X 	N-----ZC 	3 	7[4]
MVN srcbk,destbk 		Block Move Negative 	54 	Block Move 		3 	1[3]
MVP srcbk,destbk 		Block Move Positive 	44 	Block Move 		3 	1[3]
PEA addr 		Push Effective Absolute Address 	F4 	Stack (Absolute) 		3 	5
PEI (dp) 		Push Effective Indirect Address 	D4 	Stack (DP Indirect) 		2 	6[2]
PER label 		Push Effective PC Relative Indirect Address 	62 	Stack (PC Relative Long) 		3 	6
PHB 		Push Data Bank Register 	8B 	Stack (Push) 		1 	3
PHD 		Push Direct Page Register 	0B 	Stack (Push) 		1 	4
PHK 		Push Program Bank Register 	4B 	Stack (Push) 		1 	3
PHP 		Push Processor Status Register 	08 	Stack (Push) 		1 	3
PLB 		Pull Data Bank Register 	AB 	Stack (Pull) 	N-----Z- 	1 	4
PLD 		Pull Direct Page Register 	2B 	Stack (Pull) 	N-----Z- 	1 	5
PLP 		Pull Processor Status Register 	28 	Stack (Pull) 	NVMXDIZC 	1 	4
REP #const 		Reset Processor Status Bits 	C2 	Immediate 	NVMXDIZC 	2 	3
ROL dp 		Rotate Memory or Accumulator Left 	26 	Direct Page 	N-----ZC 	2 	5[2][4]
ROL A 		Rotate Memory or Accumulator Left 	2A 	Accumulator 	N-----ZC 	1 	2
ROL addr 		Rotate Memory or Accumulator Left 	2E 	Absolute 	N-----ZC 	3 	6[4]
ROL dp,X 		Rotate Memory or Accumulator Left 	36 	DP Indexed,X 	N-----ZC 	2 	6[2][4]
ROL addr,X 		Rotate Memory or Accumulator Left 	3E 	Absolute Indexed,X 	N-----ZC 	3 	7[4]
ROR dp 		Rotate Memory or Accumulator Right 	66 	Direct Page 	N-----ZC 	2 	5[2][4]
ROR A 		Rotate Memory or Accumulator Right 	6A 	Accumulator 	N-----ZC 	1 	2
ROR addr 		Rotate Memory or Accumulator Right 	6E 	Absolute 	N-----ZC 	3 	6[4]
ROR dp,X 		Rotate Memory or Accumulator Right 	76 	DP Indexed,X 	N-----ZC 	2 	6[2][4]
ROR addr,X 		Rotate Memory or Accumulator Right 	7E 	Absolute Indexed,X 	N-----ZC 	3 	7[4]
RTI 		Return from Interrupt 	40 	Stack (RTI) 	NVMXDIZC 	1 	6[7]
RTL 		Return from Subroutine Long 	6B 	Stack (RTL) 		1 	6
RTS 		Return from Subroutine 	60 	Stack (RTS) 		1 	6
SEP #const 		Set Processor Status Bits 	E2 	Immediate 	NVMXDIZC 	2 	3
STA (dp,X) 		Store Accumulator to Memory 	81 	DP Indexed Indirect,X 		2 	6[1][2]
STA sr,S 		Store Accumulator to Memory 	83 	Stack Relative 		2 	4[1]
STA dp 		Store Accumulator to Memory 	85 	Direct Page 		2 	3[1][2]
STA [dp] 		Store Accumulator to Memory 	87 	DP Indirect Long 		2 	6[1][2]
STA addr 		Store Accumulator to Memory 	8D 	Absolute 		3 	4[1]
STA long 		Store Accumulator to Memory 	8F 	Absolute Long 		4 	5[1]
STA (dp),Y 		Store Accumulator to Memory 	91 	DP Indirect Indexed, Y 		2 	6[1][2]
STA (dp) 		Store Accumulator to Memory 	92 	DP Indirect 		2 	5[1][2]
STA (sr,S),Y 		Store Accumulator to Memory 	93 	SR Indirect Indexed,Y 		2 	7[1]
STA _dp_X 		Store Accumulator to Memory 	95 	DP Indexed,X 		2 	4[1][2]
STA [dp],Y 		Store Accumulator to Memory 	97 	DP Indirect Long Indexed, Y 		2 	6[1][2]
STA addr,Y 		Store Accumulator to Memory 	99 	Absolute Indexed,Y 		3 	5[1]
STA addr,X 		Store Accumulator to Memory 	9D 	Absolute Indexed,X 		3 	5[1]
STA long,X 		Store Accumulator to Memory 	9F 	Absolute Long Indexed,X 		4 	5[1]
STP 		Stop Processor 	DB 	Implied 		1 	3[9]
STX dp 		Store Index Register X to Memory 	86 	Direct Page 		2 	3[2][8]
STX addr 		Store Index Register X to Memory 	8E 	Absolute 		3 	4[8]
STX dp,Y 		Store Index Register X to Memory 	96 	DP Indexed,Y 		2 	4[2][8]
STY dp 		Store Index Register Y to Memory 	84 	Direct Page 		2 	3[2][8]
STY addr 		Store Index Register Y to Memory 	8C 	Absolute 		3 	4[8]
STY dp,X 		Store Index Register Y to Memory 	94 	DP Indexed,X 		2 	4[2][8]
STZ dp 		Store Zero to Memory 	64 	Direct Page 		2 	3[1][2]
STZ dp,X 		Store Zero to Memory 	74 	DP Indexed,X 		2 	4[1][2]
STZ addr 		Store Zero to Memory 	9C 	Absolute 		3 	4[1]
STZ addr,X 		Store Zero to Memory 	9E 	Absolute Indexed,X 		3 	5[1]
TCD 		Transfer 16-bit Accumulator to Direct Page Register 	5B 	Implied 	N-----Z- 	1 	2
TCS 		Transfer 16-bit Accumulator to Stack Pointer 	1B 	Implied 		1 	2
TDC 		Transfer Direct Page Register to 16-bit Accumulator 	7B 	Implied 	N-----Z- 	1 	2
TRB dp 		Test and Reset Memory Bits Against Accumulator 	14 	Direct Page 	------Z- 	2 	5[2][4]
TRB addr 		Test and Reset Memory Bits Against Accumulator 	1C 	Absolute 	------Z- 	3 	6[4]
TSB dp 		Test and Set Memory Bits Against Accumulator 	04 	Direct Page 	------Z- 	2 	5[2][4]
TSB addr 		Test and Set Memory Bits Against Accumulator 	0C 	Absolute 	------Z- 	3 	6[4]
TSC 		Transfer Stack Pointer to 16-bit Accumulator 	3B 	Implied 	N-----Z- 	1 	2
TXS 		Transfer Index Register X to Stack Pointer 	9A 	Implied 		1 	2
WAI 		Wait for Interrupt 	CB 	Implied 		1 	3[10]
WDM 		Reserved for Future Expansion 	42 			2 	0[11]
XBA 		Exchange B and A 8-bit Accumulators 	EB 	Implied 	N-----Z- 	1 	3
XCE 		Exchange Carry and Emulation Flags 	FB 	Implied 	--MX---CE 	1 	2
'''

def funcReturn(): pass

class Register:
	def __init__(self, n):
		self.name = n
		self.using = False
		self.pushes = 0
	def __str__(self): return self.name
	
	def push(self): pass
	def pull(self): pass
	
	def use(self):
		if self.using:
			self.push()
			self.pushes += 1
		self.using = True
	
	def unuse(self):
		if self.pushes > 0:
			self.pull()
			self.pushes -= 1
		if self.pushes == 0:
			self.using = False

class RegPC (Register):
	def __init__(self): super().__init__("PC")
	def __setattr__(self, x, op):
		if isinstance(op, bool) and x in ["N", "V", "M", "X", "D", "I", "Z", "C", "E", "B"]:
			match x:
				case "V" if not op: general.asm.append("clv;")
				case "D": general.asm.append("sed;" if op else "cld;")
				case "I": general.asm.append("sei;" if op else "cli;")
				case "C": general.asm.append("sec;" if op else "clc;")
				case _: raise ValueError(f"Cannot {"set" if op else "clear"} {x} flag. Operation not supported.")
			return
		super().__setattr__(x, op)
	def push(self): pass
	def pull(self): pass
PC = RegPC()

class RegDP (Register):
	def __init__(self): super().__init__("DP")
	def __setattr__(self, x, op):
		super().__setattr__(x, op)
	def push(self): pass
	def pull(self): pass
DP = RegDP()

class RegA (Register):
	def __init__(self): super().__init__("A")
	def __len__(self): pass #depends on pc flag
	def __setattr__(self, x, op):
		if x == "value":
			if isinstance(op, Register):
				match op.name:
					case "X": general.asm.append("txa;")
					case "Y": general.asm.append("tya;")
			elif isinstance(op, AddressingMode):
				acceptedModes = [MODE_DIRECT_INDIRECT_X, MODE_STACK_RELATIVE, MODE_DIRECT, MODE_DIRECT_INDIRECT_LONG, MODE_IMMEDIATE,
				MODE_ABSOLUTE, MODE_ABSOLUTE_LONG, MODE_DIRECT_INDIRECT_Y, MODE_DIRECT_INDIRECT, MODE_STACK_RELATIVE_INDIRECT_Y,
				MODE_DIRECT_X, MODE_DIRECT_INDIRECT_LONG_Y, MODE_ABSOLUTE_Y, MODE_ABSOLUTE_X, MODE_ABSOLUTE_LONG_X]
				if op.mode in acceptedModes: asm(f"lda {op.swap};")
				else: catch("REGA.__SETATTR__()", f"Unaccepted addressing mode ({str(op)}).")
		super().__setattr__(x, op)
	def push(self): asm("pha;")
	def pull(self): asm("pla;")
	
	def __add__(self, val): pass
	def __radd__(self, val): pass
	def __iadd__(self, val):
		if isinstance(val, int):
			asm("inc a;" if val==1 else f"adc #{val};")
		if isinstance(val, AddressingMode):
			acceptedModes = [MODE_DIRECT_INDIRECT_X, MODE_STACK_RELATIVE, MODE_DIRECT, MODE_DIRECT_INDIRECT_LONG, MODE_IMMEDIATE,
			MODE_ABSOLUTE, MODE_ABSOLUTE_LONG, MODE_DIRECT_INDIRECT_Y, MODE_DIRECT_INDIRECT, MODE_STACK_RELATIVE_INDIRECT_Y,
			MODE_DIRECT_X, MODE_DIRECT_INDIRECT_LONG_Y, MODE_ABSOLUTE_Y, MODE_ABSOLUTE_X, MODE_ABSOLUTE_LONG_X]
			if val.mode in acceptedModes:
				if val.mode == MODE_IMMEDIATE: asm("inc a;" if val.arg=="$1" else f"adc #{val.swap};")
				else: asm(f"adc {val.swap};")
			else: catch("REGA.__IADD__()", f"Unaccepted addressing mode ({str(val)}).")
		return self
	
	def __sub__(self, val): pass
	def __rsub__(self, val): pass
	def __isub__(self, val):
		if isinstance(val, int):
			asm("dec a;" if val==1 else f"sbc #{val};")
		elif isinstance(val, AddressingMode):
			acceptedModes = [MODE_DIRECT_INDIRECT_X, MODE_STACK_RELATIVE, MODE_DIRECT, MODE_DIRECT_INDIRECT_LONG, MODE_IMMEDIATE,
			MODE_ABSOLUTE, MODE_ABSOLUTE_LONG, MODE_DIRECT_INDIRECT_Y, MODE_DIRECT_INDIRECT, MODE_STACK_RELATIVE_INDIRECT_Y,
			MODE_DIRECT_X, MODE_DIRECT_INDIRECT_LONG_Y, MODE_ABSOLUTE_Y, MODE_ABSOLUTE_X, MODE_ABSOLUTE_LONG_X]
			if val.mode in acceptedModes:
				if val.mode == MODE_IMMEDIATE: asm("dec a;" if val.arg=="$1" else f"sbc #{val.swap};")
				else: asm(f"sbc {val.swap};")
			else: catch("REGA.__ISUB__()", f"Unaccepted addressing mode ({str(val)}).")
		return self
	
	def __and__(self, val): pass
	def __rand__(self, val): pass
	def __iand__(self, val):
		if isinstance(val, int): asm(f"and #{val};")
		elif isinstance(val, AddressingMode):
			acceptedModes = [MODE_DIRECT_INDIRECT_X, MODE_STACK_RELATIVE, MODE_DIRECT, MODE_DIRECT_INDIRECT_LONG, MODE_IMMEDIATE,
			MODE_ABSOLUTE, MODE_ABSOLUTE_LONG, MODE_DIRECT_INDIRECT_Y, MODE_DIRECT_INDIRECT, MODE_STACK_RELATIVE_INDIRECT_Y,
			MODE_DIRECT_X, MODE_DIRECT_INDIRECT_LONG_Y, MODE_ABSOLUTE_Y, MODE_ABSOLUTE_X, MODE_ABSOLUTE_LONG_X]
			if val.mode in acceptedModes:
				if val.mode == MODE_IMMEDIATE: asm(f"and #{val.swap};")
				else: asm(f"and {val.swap};")
			else: catch("REGA.__IAND__()", f"Unaccepted addressing mode ({str(val)}).")
		return self
	
	def __or__(self, val): pass
	def __ror__(self, val): pass
	def __ior__(self, val):
		if isinstance(val, int): asm(f"oro #{val};")
		elif isinstance(val, AddressingMode):
			acceptedModes = [MODE_DIRECT_INDIRECT_X, MODE_STACK_RELATIVE, MODE_DIRECT, MODE_DIRECT_INDIRECT_LONG, MODE_IMMEDIATE,
			MODE_ABSOLUTE, MODE_ABSOLUTE_LONG, MODE_DIRECT_INDIRECT_Y, MODE_DIRECT_INDIRECT, MODE_STACK_RELATIVE_INDIRECT_Y,
			MODE_DIRECT_X, MODE_DIRECT_INDIRECT_LONG_Y, MODE_ABSOLUTE_Y, MODE_ABSOLUTE_X, MODE_ABSOLUTE_LONG_X]
			if val.mode in acceptedModes:
				if val.mode == MODE_IMMEDIATE: asm(f"oro #{val.swap};")
				else: asm(f"oro {val.swap};")
			else: catch("REGA.__IOR__()", f"Unaccepted addressing mode ({str(val)}).")
		return self
	
	def __xor__(self, val): pass
	def __rxor__(self, val): pass
	def __ixor__(self, val):
		if isinstance(val, int): asm(f"eor #{val};")
		elif isinstance(val, AddressingMode):
			acceptedModes = [MODE_DIRECT_INDIRECT_X, MODE_STACK_RELATIVE, MODE_DIRECT, MODE_DIRECT_INDIRECT_LONG, MODE_IMMEDIATE,
			MODE_ABSOLUTE, MODE_ABSOLUTE_LONG, MODE_DIRECT_INDIRECT_Y, MODE_DIRECT_INDIRECT, MODE_STACK_RELATIVE_INDIRECT_Y,
			MODE_DIRECT_X, MODE_DIRECT_INDIRECT_LONG_Y, MODE_ABSOLUTE_Y, MODE_ABSOLUTE_X, MODE_ABSOLUTE_LONG_X]
			if val.mode in acceptedModes:
				if val.mode == MODE_IMMEDIATE: asm(f"eor #{val.swap};")
				else: asm(f"eor {val.swap};")
			else: catch("REGA.__IXOR__()", f"Unaccepted addressing mode ({str(val)}).")
		return self
	
	def __rshift__(self, val): pass
	def __rrshift__(self, val): pass
	def __irshift__(self, val): return self
	def __lshift__(self, val): pass
	def __rlshift__(self, val): pass
	def __ilshift__(self, val): return self
	
	def __eq__(self, val): pass
	def __ne__(self, val): pass
	def __lt__(self, val): pass
	def __gt__(self, val): pass
	def __le__(self, val): pass
	def __ge__(self, val): pass
A = RegA()

class RegX (Register):
	def __init__(self): super().__init__("X")
	def __len__(self): pass #depends on pc flag
	def __setattr__(self, x, op):
		if x == "value":
			if isinstance(op, Register):
				match op.name:
					case "A": general.asm.append("tax;")
					case "Y": general.asm.append("tyx;")
					case "S": general.asm.append("tsx;")
		super().__setattr__(x, op)
	def push(self): asm("phx;")
	def pull(self): asm("plx;")
	
	def __add__(self, val): pass
	def __radd__(self, val): pass
	def __iadd__(self, val):
		global A, X
		if isinstance(val, AddressingMode) and val.mode == MODE_IMMEDIATE: val = int(val.arg[1:],16)
		if isinstance(val, int) and (val >= 1 and val <= 3): asm("inx;"*val)
		else: A.use(); A.value = X; A += val; X.value = A; A.unuse()
		return self
	
	def __sub__(self, val): pass
	def __rsub__(self, val): pass
	def __isub__(self, val):
		global A, X
		if isinstance(val, AddressingMode) and val.mode == MODE_IMMEDIATE: val = int(val.arg[1:],16)
		if isinstance(val, int) and (val >= 1 and val <= 3): asm("dex;"*val)
		else: A.use(); A.value = X; A -= val; X.value = A; A.unuse()
		return self
	
	def __and__(self, val): pass
	def __rand__(self, val): pass
	def __iand__(self, val): return self
	def __or__(self, val): pass
	def __ror__(self, val): pass
	def __ior__(self, val): return self
	def __xor__(self, val): pass
	def __rxor__(self, val): pass
	def __ixor__(self, val): return self
	
	def __rshift__(self, val): pass
	def __rrshift__(self, val): pass
	def __irshift__(self, val): return self
	def __lshift__(self, val): pass
	def __rlshift__(self, val): pass
	def __ilshift__(self, val): return self
	
	def __eq__(self, val): pass
	def __ne__(self, val): pass
	def __lt__(self, val): pass
	def __gt__(self, val): pass
	def __le__(self, val): pass
	def __ge__(self, val): pass
X = RegX()

class RegY (Register):
	def __init__(self): super().__init__("Y")
	def __len__(self): pass #depends on pc flag
	def __setattr__(self, x, op):
		if x == "value":
			if isinstance(op, Register):
				match op.name:
					case "A": general.asm.append("tay;")
					case "X": general.asm.append("txy;")
		super().__setattr__(x, op)
	def push(self): asm("phy;")
	def pull(self): asm("ply;")
	
	def __add__(self, val): pass
	def __radd__(self, val): pass
	def __iadd__(self, val):
		global A, Y
		if isinstance(val, AddressingMode) and val.mode == MODE_IMMEDIATE: val = int(val.arg[1:],16)
		if isinstance(val, int) and (val >= 1 and val <= 3): asm("iny;"*val)
		else: A.use(); A.value = Y; A += val; Y.value = A; A.unuse()
		return self
	
	def __sub__(self, val): pass
	def __rsub__(self, val): pass
	def __isub__(self, val):
		global A, Y
		if isinstance(val, AddressingMode) and val.mode == MODE_IMMEDIATE: val = int(val.arg[1:],16)
		if isinstance(val, int) and (val >= 1 and val <= 3): asm("dey;"*val)
		else: A.use(); A.value = Y; A -= val; Y.value = A; A.unuse()
		return self
	
	def __and__(self, val): pass
	def __rand__(self, val): pass
	def __iand__(self, val): return self
	def __or__(self, val): pass
	def __ror__(self, val): pass
	def __ior__(self, val): return self
	def __xor__(self, val): pass
	def __rxor__(self, val): pass
	def __ixor__(self, val): return self
	
	def __rshift__(self, val): pass
	def __rrshift__(self, val): pass
	def __irshift__(self, val): return self
	def __lshift__(self, val): pass
	def __rlshift__(self, val): pass
	def __ilshift__(self, val): return self
	
	def __eq__(self, val): pass
	def __ne__(self, val): pass
	def __lt__(self, val): pass
	def __gt__(self, val): pass
	def __le__(self, val): pass
	def __ge__(self, val): pass
Y = RegY()

class StoredValue (general.ValueHook):
	# *OBJ -> OBJ.address
	def __init__(self, nam, adr, wid, sig): super().__init__(nam, adr, wid, sig)
	def __len__(self): return super().__len__()
	
	def getBits(self, field): pass
	def getFlag(self, field): pass
	def push(self): pass
	def pull(self): pass
	
	def __add__(self, val): pass
	def __radd__(self, val): pass
	def __iadd__(self, val): return self
	def __sub__(self, val): pass
	def __rsub__(self, val): pass
	def __isub__(self, val): return self
	
	def __and__(self, val): pass
	def __rand__(self, val): pass
	def __iand__(self, val): return self
	def __or__(self, val): pass
	def __ror__(self, val): pass
	def __ior__(self, val): return self
	def __xor__(self, val): pass
	def __rxor__(self, val): pass
	def __ixor__(self, val): return self
	
	def __rshift__(self, val): pass
	def __rrshift__(self, val): pass
	def __irshift__(self, val): return self
	def __lshift__(self, val): pass
	def __rlshift__(self, val): pass
	def __ilshift__(self, val): return self
	
	def __neg__(self): pass
	def __pos__(self): pass
	def __invert__(self): pass
	def __abs__(self): pass
	
	def __eq__(self, val): pass
	def __ne__(self, val): pass
	def __lt__(self, val): pass
	def __gt__(self, val): pass
	def __le__(self, val): pass
	def __ge__(self, val): pass

class ubyte (StoredValue):
	def __init__(self, nam, adr): super().__init__(nam, adr, 1, False)
class ushort (StoredValue):
	def __init__(self, nam, adr): super().__init__(nam, adr, 2, False)
class uint (StoredValue):
	def __init__(self, nam, adr): super().__init__(nam, adr, 4, False)
class sbyte (StoredValue):
	def __init__(self, nam, adr): super().__init__(nam, adr, 1, True)
class sshort (StoredValue):
	def __init__(self, nam, adr): super().__init__(nam, adr, 2, True)
class sint (StoredValue):
	def __init__(self, nam, adr): super().__init__(nam, adr, 4, True)

# CONSTANT SIZE
class array:
	def __init__(self, typ, vals): #vals can be either an array or the size of the array
		if not isinstance(typ, StoredValue): raise TypeError("Array arg 0 must be of class StoredValue.")
		self.type = typ
		self.length = len(vals) if isinstance(vals, list) else vals
		if isinstance(vals, list): pass
	def __len__(self): return len(self.type)*self.length
	
	def __getitem__(self, x): pass
	def __setitem__(self, x, val): pass
	def __contains__(self, val): pass

# CHANGABLE SIZE
class vector:
	def resize(self):
		pass
	
	def __init__(self, typ, vals=[], countStr=1):
		if not isinstance(typ, StoredValue): raise TypeError("Array arg 0 must be of class StoredValue.")
		if not (isinstance(vals, list) and all(isinstance(i, int) for i in vals)): raise TypeError("Array arg 1 must be a list of ints.")
		self.type = typ
		self.length = siz
		self.countStride = StoredValue(None, self.type.address, countStr, False)
	
	def __getitem__(self, x): pass
	def __setitem__(self, x, val): pass
	def __contains__(self, val): pass

class pointer (general.PointerHook):
	def __init__(self, nam, adr, sval): super().__init__(nam, adr, sval)
	def __len__(self): return super().__len__()
	def push(self): pass
	def pull(self): pass
	
	def __add__(self, val): self.address.__add__(val)
	def __radd__(self, val): self.address.__radd__(val)
	def __iadd__(self, val): self.address.__iadd__(val)
	def __sub__(self, val): self.address.__sub__(val)
	def __rsub__(self, val): self.address.__rsub__(val)
	def __isub__(self, val): self.address.__isub__(val)
	def __and__(self, val): self.address.__and__(val)
	def __rand__(self, val): self.address.__rand__(val)
	def __iand__(self, val): self.address.__iand__(val)
	def __or__(self, val): self.address.__or__(val)
	def __ror__(self, val): self.address.__ror__(val)
	def __ior__(self, val): self.address.__ior__(val)
	def __xor__(self, val): self.address.__xor__(val)
	def __rxor__(self, val): self.address.__rxor__(val)
	def __ixor__(self, val): self.address.__ixor__(val)
	def __rshift__(self, val): self.address.__rshift__(val)
	def __rrshift__(self, val): self.address.__rrshift__(val)
	def __irshift__(self, val): self.address.__irshift__(val)
	def __lshift__(self, val): self.address.__lshift__(val)
	def __rlshift__(self, val): self.address.__rlshift__(val)
	def __ilshift__(self, val): self.address.__ilshift__(val)
	def __neg__(self): self.address.__neg__()
	def __pos__(self): self.address.__pos__()
	def __invert__(self): self.address.__invert__()
	def __abs__(self): self.address.__abs__()
	def __eq__(self, val): self.address.__eq__(val)
	def __ne__(self, val): self.address.__ne__(val)
	def __lt__(self, val): self.address.__lt__(val)
	def __gt__(self, val): self.address.__gt__(val)
	def __le__(self, val): self.address.__le__(val)
	def __ge__(self, val): self.address.__ge__(val)

class AddressingMode:
	def __init__(self, md):
		self.unresolvedText = md
		self.resolvedText = resolveMode(self.unresolvedText)
		self.mode, self.arg = identifyMode(self.resolvedText)
		self.swap = modeSyntax(self.mode, self.arg) if (self.mode != None and self.arg != None) else None
		print(self)
	def __str__(self): return f"Address mode: {ADDRESSING_MODES[self.mode]["name"].capitalize() if self.mode != None else "None"}, {self.arg}; From {self.unresolvedText} => {self.resolvedText}"
	def __setattr__(self, x, op):
		if x == "value":
			if isinstance(op, Register):
				match op.name:
					case "A": pass
					# STORE OPERATIONS
		super().__setattr__(x, op)
	
	def __add__(self, val): pass
	def __radd__(self, val): pass
	def __iadd__(self, val): return self
	def __sub__(self, val): pass
	def __rsub__(self, val): pass
	def __isub__(self, val): return self
	def __and__(self, val): pass
	def __rand__(self, val): pass
	def __iand__(self, val): return self
	def __or__(self, val): pass
	def __ror__(self, val): pass
	def __ior__(self, val): return self
	def __xor__(self, val): pass
	def __rxor__(self, val): pass
	def __ixor__(self, val): return self
	def __rshift__(self, val): pass
	def __rrshift__(self, val): pass
	def __irshift__(self, val): return self
	def __lshift__(self, val): pass
	def __rlshift__(self, val): pass
	def __ilshift__(self, val): return self
	def __neg__(self): pass
	def __pos__(self): pass
	def __invert__(self): pass
	def __abs__(self): pass
	def __eq__(self, val): pass
	def __ne__(self, val): pass
	def __lt__(self, val): pass
	def __gt__(self, val): pass
	def __le__(self, val): pass
	def __ge__(self, val): pass

def goto(lb): pass

#[{type}, {args}, {lbStart}, {lbEnd}]
scopeStack = []

def scopeStart(t, a, lbStart, lbEnd): pass
def scopeEnd(): pass