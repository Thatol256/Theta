import general

# TODO: STZ DOESN'T SUPPORT 3-BYTE ADDRESSES, REVIEW ALL USES OF THE INSTRUCTION
# TODO: INDIRECT ADDRESSING MODES DON'T TAKE INTO CONSIDERATION THE FINAL VALUE MIGHT NOT BE THE SAME STRIDE AS THE ARG
#       POTENTIAL SOLUTION: ONLY ALLOW POINTER OBJECTS TO USE INDIRECT ADDRESSING MODES?

def asm(op): general.addAsm(op)
def raw(txt): general.addRaw(txt)
def wait(): asm("wai;")
def nop(): asm("nop;")
def stop(): asm("stp;")

def catch(a, b): general.catch(a, b)

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
	{ "name": "immediate",                 "match": f"({RE_INT})",                      "swap": "#1",       "maximumSize": 2 },
	{ "name": "relative",                  "match": fr"PC([\+\-]{RE_UINT})",            "swap": "#1",       "maximumSize": 1 },
	{ "name": "direct",                    "match": f"#({RE_UINT})",                    "swap": "1",        "maximumSize": 1 },
	{ "name": "direct indirect",           "match": f"&2:#({RE_UINT})",                 "swap": "(1)",      "maximumSize": 1 },
	{ "name": "direct indirect long",      "match": f"&3:#({RE_UINT})",                 "swap": "[1]",      "maximumSize": 1 },
	{ "name": "direct x",                  "match": fr"#({RE_UINT})\+X",                "swap": "1,x",      "maximumSize": 1 },
	{ "name": "direct y",                  "match": fr"#({RE_UINT})\+Y",                "swap": "1,y",      "maximumSize": 1 },
	{ "name": "direct indirect x",         "match": fr"&2:\(#({RE_UINT})\+X\)",         "swap": "(1,x)",    "maximumSize": 1 },
	{ "name": "direct indirect y",         "match": fr"&2:\(#({RE_UINT})\)\+Y",         "swap": "(1),y",    "maximumSize": 1 },
	{ "name": "direct indirect long y",    "match": fr"&3:\(#({RE_UINT})\)\+Y",         "swap": "[1],y",    "maximumSize": 1 },
	{ "name": "absolute",                  "match": f"#({RE_UINT})",                    "swap": "1",        "maximumSize": 2 },
	{ "name": "absolute x",                "match": fr"#({RE_UINT})\+X",                "swap": "1,x",      "maximumSize": 2 },
	{ "name": "absolute y",                "match": fr"#({RE_UINT})\+Y",                "swap": "1,y",      "maximumSize": 2 },
	{ "name": "absolute long",             "match": f"#({RE_UINT})",                    "swap": "1",        "maximumSize": 3 },
	{ "name": "absolute long x",           "match": fr"#({RE_UINT})\+X",                "swap": "1,x",      "maximumSize": 3 },
	{ "name": "absolute indirect",         "match": f"&2:#({RE_UINT})",                 "swap": "(1)",      "maximumSize": 2 },
	{ "name": "absolute indirect long",    "match": f"&3:#({RE_UINT})",                 "swap": "[1]",      "maximumSize": 2 },
	{ "name": "absolute indirect x",       "match": fr"&2:\(#({RE_UINT})\+X\)",         "swap": "(1,x)",    "maximumSize": 2 },
	{ "name": "stack relative",            "match": fr"([\+\-]{RE_UINT})\+S",           "swap": "#1,s",     "maximumSize": 1 },
	{ "name": "stack relative indirect y", "match": fr"&2:\(([\+\-]{RE_UINT})\+S\)\+Y", "swap": "(#1,s),y", "maximumSize": 1 }
]

# if a variable name is present in a string, this returns the storedvalue object
def getEmbeddedVariable(txt):
	varNames = [x.name for x in general.VARIABLES]
	for i, v in enumerate(varNames):
		if v in txt: return general.VARIABLES[i]
	return None

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
	var = getEmbeddedVariable(txt)
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

DEFAULT_MODES = [MODE_DIRECT_INDIRECT_X, MODE_STACK_RELATIVE, MODE_DIRECT, MODE_DIRECT_INDIRECT_LONG, MODE_IMMEDIATE,
MODE_ABSOLUTE, MODE_ABSOLUTE_LONG, MODE_DIRECT_INDIRECT_Y, MODE_DIRECT_INDIRECT, MODE_STACK_RELATIVE_INDIRECT_Y,
MODE_DIRECT_X, MODE_DIRECT_INDIRECT_LONG_Y, MODE_ABSOLUTE_Y, MODE_ABSOLUTE_X, MODE_ABSOLUTE_LONG_X]

class AddressingMode:
	def __init__(self, md):
		self.unresolvedText = md
		self.resolvedText = resolveMode(self.unresolvedText)
		self.mode, self.arg = identifyMode(self.resolvedText)
		self.swap = modeSyntax(self.mode, self.arg) if (self.mode != None and self.arg != None) else None
	def __str__(self): return f"Address mode: {ADDRESSING_MODES[self.mode]["name"].capitalize() if self.mode != None else "None"}, {self.arg}; From {self.unresolvedText} => {self.resolvedText}"
	
	def __eq__(self, val):
		if isinstance(val, int): return self.mode == MODE_IMMEDIATE and mode.swap == f"#${hex(val)[2:]}"
		elif isinstance(val, str): return self.swap == AddressingMode(val).swap
		elif isinstance(val, AddressingMode): return self.swap == val.swap
		return False

def adsmInt(val):
	if isinstance(val, int): return val
	if isinstance(val, AddressingMode):
		if val.mode == MODE_IMMEDIATE:
			return int(val.arg,16)
	return None

# ctx - context function (for error handling) (e.g. "__IADD__")
# val - arg
# opc - opcode
# modes - accepted addressing modes
# letNAdsm - if True, returns False if type isn't an addressing mode, otherwise throw error
# letNMode - if True, returns False if addressing mode unaccepted, otherwise throw error
def opSwap(ctx, val, opc, modes, letNAdsm = False, letNMode = False):
	if isinstance(val, general.ValueHook): val = val.address
	if isinstance(val, int): val = AddressingMode(str(val))
	if isinstance(val, AddressingMode):
		if val.mode in modes:
			asm(f"{opc} {val.swap};")
			return True
		if not letNMode: catch(f"{ctx}->OPSWAP()", f"Unaccepted addressing mode ({val}).")
		return False
	if not letNAdsm: catch(f"{ctx}->OPSWAP()", f"Val ({val}) is not a valid type ({type(val)}).")
	return False

'''
VAR -> #VAR.address
*VAR -> VAR.address
&(*VAR + X) -> &VAR.width:(VAR.address + X)
*PTR -> PTR.address
PTR -> #PTR.address
&PTR -> &PTR.reference.width:#PTR.address
&(*PTR + X) -> &PTR.reference.width:(PTR.address + X)

INSTRUCTIONS LEFT:
BIT dp 		Test Bits 	24 	Direct Page 	NV----Z- 	2 	3[1][2]
BIT addr 		Test Bits 	2C 	Absolute 	NV----Z- 	3 	4[1]
BIT dp,X 		Test Bits 	34 	DP Indexed,X 	NV----Z- 	2 	4[1][2]
BIT addr,X 		Test Bits 	3C 	Absolute Indexed,X 	NV----Z- 	3 	4[1][3]
BIT #const 		Test Bits 	89 	Immediate 	------Z- 	2[12] 	2[1]
BRA nearlabel 		Branch Always 	80 	Program Counter Relative 		2 	3[6]
BRK 		Break 	00 	Stack/Interrupt 	----DI-- 	2[13] 	7[7]
BRL label 		Branch Long Always 	82 	Program Counter Relative Long 		3 	4
COP #const 		Co-Processor 	02 	Stack/Interrupt 	----DI-- 	2[13] 	7[7]
JMP addr 		Jump 	4C 	Absolute 		3 	3
JMP long 	JML 	Jump 	5C 	Absolute Long 		4 	4
JMP (addr) 		Jump 	6C 	Absolute Indirect 		3 	5
JMP (addr,X) 		Jump 	7C 	Absolute Indexed Indirect 		3 	6
JMP [addr] 	JML 	Jump 	DC 	Absolute Indirect Long 		3 	6
JSR addr 		Jump to Subroutine 	20 	Absolute 		3 	6
JSR long 	JSL 	Jump to Subroutine 	22 	Absolute Long 		4 	8
JSR (addr,X)) 		Jump to Subroutine 	FC 	Absolute Indexed Indirect 		3 	8
MVN srcbk,destbk 		Block Move Negative 	54 	Block Move 		3 	1[3]
MVP srcbk,destbk 		Block Move Positive 	44 	Block Move 		3 	1[3]
PEA addr 		Push Effective Absolute Address 	F4 	Stack (Absolute) 		3 	5
PEI (dp) 		Push Effective Indirect Address 	D4 	Stack (DP Indirect) 		2 	6[2]
PER label 		Push Effective PC Relative Indirect Address 	62 	Stack (PC Relative Long) 		3 	6
PHB 		Push Data Bank Register 	8B 	Stack (Push) 		1 	3
PHK 		Push Program Bank Register 	4B 	Stack (Push) 		1 	3
PLB 		Pull Data Bank Register 	AB 	Stack (Pull) 	N-----Z- 	1 	4
REP #const 		Reset Processor Status Bits 	C2 	Immediate 	NVMXDIZC 	2 	3
RTI 		Return from Interrupt 	40 	Stack (RTI) 	NVMXDIZC 	1 	6[7]
RTL 		Return from Subroutine Long 	6B 	Stack (RTL) 		1 	6
RTS 		Return from Subroutine 	60 	Stack (RTS) 		1 	6
SEP #const 		Set Processor Status Bits 	E2 	Immediate 	NVMXDIZC 	2 	3
TCD 		Transfer 16-bit Accumulator to Direct Page Register 	5B 	Implied 	N-----Z- 	1 	2
TCS 		Transfer 16-bit Accumulator to Stack Pointer 	1B 	Implied 		1 	2
TDC 		Transfer Direct Page Register to 16-bit Accumulator 	7B 	Implied 	N-----Z- 	1 	2
TRB dp 		Test and Reset Memory Bits Against Accumulator 	14 	Direct Page 	------Z- 	2 	5[2][4]
TRB addr 		Test and Reset Memory Bits Against Accumulator 	1C 	Absolute 	------Z- 	3 	6[4]
TSB dp 		Test and Set Memory Bits Against Accumulator 	04 	Direct Page 	------Z- 	2 	5[2][4]
TSB addr 		Test and Set Memory Bits Against Accumulator 	0C 	Absolute 	------Z- 	3 	6[4]
TSC 		Transfer Stack Pointer to 16-bit Accumulator 	3B 	Implied 	N-----Z- 	1 	2
TXS 		Transfer Index Register X to Stack Pointer 	9A 	Implied 		1 	2
WDM 		Reserved for Future Expansion 	42 			2 	0[11]
XBA 		Exchange B and A 8-bit Accumulators 	EB 	Implied 	N-----Z- 	1 	3
XCE 		Exchange Carry and Emulation Flags 	FB 	Implied 	--MX---CE 	1 	2
'''

class RegPC (general.Register):
	def __init__(self): super().__init__("PC", 2)
	def __setattr__(self, x, op):
		xIsFlag = x in ["N", "V", "M", "X", "D", "I", "Z", "C", "E", "B"]
		legalIB = isinstance(op, bool) or (isinstance(op, int) and op in [0, 1])
		legalAdsm = isinstance(op, AddressingMode) and op.resolvedText in ["True", "False", "$0", "$1"]
		if (legalIB or legalAdsm) and xIsFlag:
			if legalAdsm: op = op.resolvedText in ["True", "$1"]
			if legalIB: op = op in [True, 1]
			match x:
				case "V" if not op: asm("clv;")
				case "D": asm("sed;" if op else "cld;")
				case "I": asm("sei;" if op else "cli;")
				case "C": asm("sec;" if op else "clc;")
				case _: raise ValueError(f"Cannot {"set" if op else "clear"} {x} flag. Operation not supported.")
			return
		super().__setattr__(x, op)
	def push(self): asm("php;")
	def pull(self): asm("plp;")
PC = RegPC()

class RegDP (general.Register):
	def __init__(self): super().__init__("DP", 1)
	def __setattr__(self, x, op):
		super().__setattr__(x, op)
	def push(self): asm("phd;")
	def pull(self): asm("pld;")
DP = RegDP()

class RegA (general.Register):
	def __init__(self): super().__init__("A", 1) # width can be changed with an instruction; don't forget!
	def __len__(self): pass #depends on pc flag
	def __setattr__(self, x, op):
		if x == "value":
			if isinstance(op, general.Register):
				match op.name:
					case "X": general.asm.append("txa;")
					case "Y": general.asm.append("tya;")
			else: opSwap("REGA.__SETATTR__()", op, "lda", DEFAULT_MODES, True)
		super().__setattr__(x, op)
	def push(self): asm("pha;")
	def pull(self): asm("pla;")
	
	def __iadd__(self, val):
		if val == 1: asm("inc a;")
		else: opSwap("REGA.__IADD__()", val, "adc", DEFAULT_MODES)
		return self
	def __isub__(self, val):
		if val == 1: asm("dec a;")
		else: opSwap("REGA.__ISUB__()", val, "sbc", DEFAULT_MODES)
		return self
	def __iand__(self, val): opSwap("REGA.__IAND__()", val, "and", DEFAULT_MODES); return self
	def __ior__(self, val): opSwap("REGA.__IOR__()", val, "oro", DEFAULT_MODES); return self
	def __ixor__(self, val): opSwap("REGA.__IXOR__()", val, "eor", DEFAULT_MODES); return self
	
	def shiftLeft(self, val):
		if n := adsmInt(val) != None: asm(f"asl a;"*n)
		else: opSwap("REGA.SHIFTLEFT()", val, "asl", [MODE_DIRECT, MODE_ABSOLUTE, MODE_DIRECT_X, MODE_ABSOLUTE_X])
	def shiftRight(self, val):
		if n := adsmInt(val) != None: asm(f"lsr a;"*n)
		else: opSwap("REGA.SHIFTRIGHT()", val, "lsr", [MODE_DIRECT, MODE_ABSOLUTE, MODE_DIRECT_X, MODE_ABSOLUTE_X])
	def rotateLeft(self, val):
		if n := adsmInt(val) != None: asm(f"rol a;"*n)
		else: opSwap("REGA.ROTATELEFT()", val, "rol", [MODE_DIRECT, MODE_ABSOLUTE, MODE_DIRECT_X, MODE_ABSOLUTE_X])
	def rotateRight(self, val):
		if n := adsmInt(val) != None: asm(f"ror a;"*n)
		else: opSwap("REGA.ROTATERIGHT()", val, "ror", [MODE_DIRECT, MODE_ABSOLUTE, MODE_DIRECT_X, MODE_ABSOLUTE_X])
	
	def __irshift__(self, val): self.shiftRight(val); return self
	def __ilshift__(self, val): self.shiftLeft(val); return self
	
	def compare(self, op): opSwap("REGA.__COMPARE__()", val, "cmp", DEFAULT_MODES)
A = RegA()

class RegX (general.Register):
	def __init__(self): super().__init__("X", 2)
	def __len__(self): pass #depends on pc flag
	def __setattr__(self, x, op):
		if x == "value":
			if isinstance(op, general.Register):
				match op.name:
					case "A": general.asm.append("tax;")
					case "Y": general.asm.append("tyx;")
					case "S": general.asm.append("tsx;")
			else: opSwap("REGX.__SETATTR__()", op, "ldx", [MODE_IMMEDIATE, MODE_DIRECT, MODE_ABSOLUTE, MODE_DIRECT_Y, MODE_ABSOLUTE_Y], True)
		super().__setattr__(x, op)
	def push(self): asm("phx;")
	def pull(self): asm("plx;")
	
	def __iadd__(self, val):
		global A, X
		if n := adsmInt(val) != None: asm(f"inx;"*n)
		else: A.use(); A.value = X; A += val; X.value = A; A.unuse()
		return self
	def __isub__(self, val):
		global A, X
		if n := adsmInt(val) != None: asm(f"dex;"*n)
		else: A.use(); A.value = X; A += val; X.value = A; A.unuse()
		return self
	
	# def __iand__(self, val): return self
	# def __ior__(self, val): return self
	# def __ixor__(self, val): return self
	# def __irshift__(self, val): return self
	# def __ilshift__(self, val): return self
	
	def compare(self, op): opSwap("REGX.__COMPARE__()", val, "cpx", [MODE_IMMEDIATE, MODE_DIRECT, MODE_ABSOLUTE])
X = RegX()

class RegY (general.Register):
	def __init__(self): super().__init__("Y", 2)
	def __len__(self): pass #depends on pc flag
	def __setattr__(self, x, op):
		if x == "value":
			if isinstance(op, general.Register):
				match op.name:
					case "A": general.asm.append("tay;")
					case "X": general.asm.append("txy;")
			else: opSwap("REGY.__SETATTR__()", op, "ldy", [MODE_IMMEDIATE, MODE_DIRECT, MODE_ABSOLUTE, MODE_DIRECT_X, MODE_ABSOLUTE_X], True)
		super().__setattr__(x, op)
	def push(self): asm("phy;")
	def pull(self): asm("ply;")
	
	def __iadd__(self, val):
		global A, Y
		if n := adsmInt(val) != None: asm(f"iny;"*n)
		else: A.use(); A.value = X; A += val; X.value = A; A.unuse()
		return self
	def __isub__(self, val):
		global A, Y
		if n := adsmInt(val) != None: asm(f"dey;"*n)
		else: A.use(); A.value = X; A += val; X.value = A; A.unuse()
		return self
	
	# def __iand__(self, val): return self
	# def __ior__(self, val): return self
	# def __ixor__(self, val): return self
	# def __irshift__(self, val): return self
	# def __ilshift__(self, val): return self
	
	def compare(self, op): opSwap("REGY.__COMPARE__()", val, "cpy", [MODE_IMMEDIATE, MODE_DIRECT, MODE_ABSOLUTE])
Y = RegY()

class StoredValue (general.ValueHook):
	# *OBJ -> OBJ.address
	def __init__(self, nam, adr, wid, sig): super().__init__(nam, adr, wid, sig)
	def __len__(self): return super().__len__()
	
	# val [int/bool/addressingmode/register/storedvalue] = Value to assign to the variable
	# mode [=/+=/-= etc.]
	# ctx [str/storedvalue/addressingmode] = The context in which it's used (VAR =, &VAR =, VAR + X =, etc.)
	def assign(self, val, mode, ctx):
		# info collection (oh isinstance by beloved, you will never understand the horrors that is this function)
		if isinstance(val, bool): val = 1 if val == True else 0
		elif isinstance(val, StoredValue): val = AddressingMode(val.name)
		if isinstance(ctx, str): ctx = AddressingMode(ctx)
		elif isinstance(ctx, StoredValue): ctx = AddressingMode(ctx.name)
		simpleContext = ctx.unresolvedText == self.name
		directAssign = mode == "="
		
		if not directAssign:
			assignMap = {"+=": "adc", "-=": "sbc", "<<=": "asl", ">>=": "lsr", "&=": "and", "|=": "oro", "^=": "eor"}
			if not mode in assignMap.keys(): catch("STOREDVALUE.ASSIGN()", f"Mode {mode} not valid.")
		
		def offsetAddress(adsm, ind):
			if isinstance(adsm, AddressingMode): return AddressingMode(adsm.unresolvedText.replace(self.name, "#0x"+hex(self.address+ind)[2:]))
			else: return AddressingMode("#0x"+hex(addr+ind)[2:])
		def transferSet(fr, to): # given the widths of two values that are being transferred, this tells you which byte in each value should be transferred. None means transfer a 0
			# examples: (assumes A is 1 byte)
			# 4, 2 ---> ([2, 3], [0, 1])
			# 3, 5 ---> ([None, None, 0, 1, 2], [0, 1, 2, 3, 4])
			# 2, 2 ---> ([0, 1], [0, 1])
			if fr == to: return (range(fr), range(to), A.width)
			elif fr > to: return (range(fr-to, fr, A.width), range(0, to, A.width))
			return ([None]*((to-fr)//A.width)+range(0, fr, A.width), range(0, to, A.width))
		def minimumWidth(v):
			x = 1
			while True:
				if v < 256**x: return x
				x += 1
		
		if isinstance(val, int): # ??? OP NUM
			if self.width // A.width != self.width / A.width: catch("STOREDVALUE.ASSIGN()", f"Module doesn't support transfer from a register ({str(A)}) with a width that is not a multiple of the destination's width ({str(self)}). This can be fixed by using the 8-bit mode on the respective register.")
			vBytes = [(val>>(8*A.width*i))&sum([0xFF<<(8*j) for j in range(A.width)]) for i in range(self.width//A.width)]
			if len(vBytes) < self.width: vBytes = [0 for i in range((self.width-len(vBytes))//A.width)] + vBytes
			if val != 0: A.use()
			if directAssign:
				for i, b in enumerate(vBytes):
					if b == 0: asm(f"stz {offsetAddress(ctx, i*A.width).swap};")
					else: A.value = b; asm(f"sta {offsetAddress(ctx, i*A.width).swap};")
			else:
				if val == 0: return
				if assignMap[mode] in ["asl", "asr"]:
					for i in range(val):
						PC.C = False
						for b in range(len(vBytes)):
							asm(f"{assignMap[mode]} {offsetAddress(ctx, i*A.width).swap};")
				else:
					PC.C = False
					for i, b in enumerate(vBytes):
						A.value = offsetAddress(ctx, i*A.width);
						asm(f"{assignMap[mode]} {"0x"+hex(b)[2:]};")
						asm(f"sta {offsetAddress(ctx, i*A.width).swap};")
			if val != 0: A.unuse()
		elif isinstance(val, general.Register): # ??? OP REG
			if not directAssign: catch("STOREDVALUE.ASSIGN()", f"Module doesn't support transfer from a register ({str(val)}) using non-direct assignment ({str(ctx)}).")
			if self.width // A.width != self.width / A.width: catch("STOREDVALUE.ASSIGN()", f"Module doesn't support transfer from a register ({str(A)}) with a width that is not a multiple of the destination's width ({str(self)}). This can be fixed by using the 8-bit mode on the respective register.")
			units = max(self.width, val.width) // A.width
			zeros = ((self.width - val.width) // A.width) if val.width < self.width else 0
			empties = ((val.width - width.width) // A.width) if val.width > self.width else 0
			transfers = self.width // A.width - zeros
			if val.name == "A" or (val.name in ["X", "Y"] and minimumWidth(self.address) <= 2 and empties == 0):
				for i in range(zeros): asm(f"stz {offsetAddress(ctx, i*A.width).swap};")
				asm(f"st{val.name.lower()} {offsetAddress(ctx, zeros*A.width).swap};")
			else:
				if self.width // A.width != self.width / A.width: catch("STOREDVALUE.ASSIGN()", f"Module doesn't support transfer from a register ({str(A)}) with a width that is not a multiple of the destination's width ({str(self)}). This can be fixed by using the 8-bit mode on the respective register.")
				A.use()
				val.push()
				for i in range(transfers): A.pull(); asm(f"sta {offsetAddress(ctx, i*A.width).swap};")
				for i in range(zeros): asm(f"stz {offsetAddress(ctx, i*A.width).swap};")
				for i in range(empties): A.pull()
				A.unuse()
		elif isinstance(val, AddressingMode): # ??? OP ADSR
			if self.width // A.width != self.width / A.width: catch("STOREDVALUE.ASSIGN()", f"Module doesn't support transfer from a register ({str(A)}) with a width that is not a multiple of the destination's width ({str(self)}). This can be fixed by using the 8-bit mode on the respective register.")
			ctxVar = getEmbeddedVariable(ctx.name)
			A.use()
			if directAssign:
				for f, t in transferSet(ctxVar.width, self.width):
					if f == None: asm(f"stz {offsetAddress(ctx, t).swap};")
					else: A.value = offsetAddress(val, f); asm(f"sta {offsetAddress(ctx, t).swap};")
			else:
				if assignMap[mode] in ["asl", "asr"]: catch("STOREDVALUE.ASSIGN()", f"Module doesn't support variable bit shifting ({str(ctx)} {mode} {str(val)}).")
				PC.C = False
				for f, t in transferSet(ctxVar.width, self.width):
					A.value = offsetAddress(ctx, t*A.width);
					asm(f"{assignMap[mode]} {offsetAddress(val, f*A.width).swap};")
					asm(f"sta {offsetAddress(ctx, i*A.width).swap};")
			A.unuse()
		
	def getBits(self, field): pass
	def getFlag(self, field): pass
	def push(self): pass
	def pull(self): pass
	
	def __add__(self, val): pass
	def __radd__(self, val): pass
	def __iadd__(self, val): self.assign(val, "+=", self.name); return self
	def __sub__(self, val): pass
	def __rsub__(self, val): pass
	def __isub__(self, val): self.assign(val, "-=", self.name); return self
	def __and__(self, val): pass
	def __rand__(self, val): pass
	def __iand__(self, val): self.assign(val, "&=", self.name); return self
	def __or__(self, val): pass
	def __ror__(self, val): pass
	def __ior__(self, val): self.assign(val, "|=", self.name); return self
	def __xor__(self, val): pass
	def __rxor__(self, val): pass
	def __ixor__(self, val): self.assign(val, "^=", self.name); return self
	def __rshift__(self, val): pass
	def __rrshift__(self, val): pass
	def __irshift__(self, val): self.assign(val, ">>=", self.name); return self
	def __lshift__(self, val): pass
	def __rlshift__(self, val): pass
	def __ilshift__(self, val): self.assign(val, "<<=", self.name); return self
	
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

def funcReturnrti(): asm("rti;")

def goto(lb):
	if not isinstance(lb, Label): catch("GOTO()", f"Arg must be of type Label. Got ({type(lb)})")
	asm(f"jmp {lb.name};")

# DICTIONARY
# type = "func/while/if..."
# condition
# name = {func name}
# labelStart
# labelEnd
# args
# return
scopeStack = []

# CONDITIONS: {FLAG/REG/ADSR} {==/!=/>/</>=/<=} {VAL/ADSR} {LABEL} {REVERSE}
def runCondition(cond, lb, rev):
	# with the compare operator, the left side is subtracted by the right (e.g. cmp $5 => A - $5)
	# A > 5 => CMP 5; BCS LBL; BEQ LBL
	mat = re.search(r"([^=!<>]+)(==|!=|<=?|>=?)([^=!<>]+)", cond)
	if mat == None: catch("", f"Condition ({cond}) not matched.")
	lv = mat.group(1).strip()
	con = mat.group(2).strip()
	rv = mat.group(3).strip()
	adsm = AddressingMode(lv)
	if rv in ["True", "true", "1", 1]: rv = True
	if rv in ["False", "false", "0", 0]: rv = False
	if adsm.mode != None: A.use(); A.value = adsm; A.unuse(); lv = "A"
	if lv in REGISTERS:
		baseOp = "cmp" if lv == "A" else f"cp{lv.lower()}"
		if rv == True: rv = 1
		if rv == False: rv = 0
		rAdsm = AddressingMode(str(rv))
		asm(f"{baseOp} {rAdsm.swap};")
		if rev:
			match (con):
				case "==": asm(f"bne {lb};")
				case "!=": asm(f"beq {lb};")
				case ">": asm(f"bcs {lb}; beq {lb};")
				case "<": asm(f"bcc {lb}; beq {lb};")
				case ">=": asm(f"bcs {lb};")
				case "<=": asm(f"bcc {lb};")
		else:
			match (con):
				case "==": asm(f"beq {lb};")
				case "!=": asm(f"bne {lb};")
				case ">": asm(f"bcc {lb};")
				case "<": asm(f"bcs {lb};")
				case ">=": asm(f"bcc {lb}; beq {lb};")
				case "<=": asm(f"bcs {lb}; beq {lb};")
	elif isinstance(rv, bool) and con in ["==", "!="] and lv in [f"PC.{x}" for x in "CNZV"]:
		if con == "!=": rev = not rev
		match (lv[-1]):
			case "C": asm(f"{"bcs" if rv ^ rev else "bcc"} {lb}")
			case "N": asm(f"{"bmi" if rv ^ rev else "bpl"} {lb}")
			case "Z": asm(f"{"beq" if rv ^ rev else "bne"} {lb}")
			case "V": asm(f"{"bvs" if rv ^ rev else "bvc"} {lb}")
	else: catch("RUNCONDITION()", f"Could not identify condition type ({lv} {con} {rv}).")

def funcStart(name, ret, args, sId, eId): pass
def conditionStart(kind, cond, sId, eId): pass

def loopStart(kind, cond, sId, eId):
	if not kind in ["for", "while", "dowhile"]: catch("LOOPSTART()", f"Unknown loop type ({kind}).")
	if kind == "while": runCondition(cond, eId, True)

def funcEnd(): pass
def conditionEnd(): pass

def loopEnd():
	scope = scopeStack[-1]
	if scope["type"] == "while":
		asm(f"bra {scope["labelStart"]}")
	elif scope["type"] in ["for", "dowhile"]:
		runCondition(scope["condition"], scope["labelStart"], False)
	else: catch("LOOPEND()", f"Scope type ({scope["type"]}) not recognized.")

# "dowhile", "while", "for", "elseif", "if", "else", "func"

# LOOPS / CONDITIONALS: scopeStart({name}, {condition}, {start id}, {end id})
# FUNCTIONS:            scopeStart([{return type}, {func name}], [{arg declarations}], {start id}, {end id})
TYPES_LOOP = ["while", "dowhile", "for"]
TYPES_COND = ["if", "else", "elseif"]
def scopeStart(t, a, lbStart, lbEnd):
	if not (isinstance(lbStart, str) and isinstance(lbEnd, str)): catch("SCOPESTART()", f"Final two arguments ({lbStart}, {lbEnd}) must be strings.")
	if isinstance(t, str) and isinstance(a, str) and t in TYPES_LOOP + TYPES_COND:
		scopeStack.append({"type": t, "condition": a, "labelStart": lbStart, "labelEnd": lbEnd})
		if t in TYPES_LOOP: loopStart(t, a, lbStart, lbEnd)
		else: conditionStart(t, a, lbStart, lbEnd)
	elif isinstance(t, list) and isinstance(a, list):
		if len(t) != 2: catch("SCOPESTART()", "Function signature must have two arguments.")
		if not isinstance(t[0], str) or not isinstance(t[1], str): catch("SCOPESTART()", "Function signature argument must be all strings.")
		if any([not isinstance(x, str) for x in a]): catch("SCOPESTART()", "Function arguments must be all strings.")
		scopeStack.append({"type": "func", "return": t[0], "name": t[1], "args": a, "labelStart": lbStart, "labelEnd": lbEnd})
		funcStart(t[1], t[0], a, lbStart, lbEnd)
	else: catch("SCOPESTART()", "Unrecognized scope type.")

def scopeEnd():
	if len(scopeStack) < 1: catch("SCOPEEND()", "No scopes are open.")
	scopeType = scopeStack[-1]["type"]
	if scopeType in TYPES_LOOP: loopEnd()
	elif scopeType in TYPES_COND: conditionEnd()
	elif scopeType == "func": funcEnd()
	else: catch("SCOPEEND()", f"Scope type ({scopeType}) not recognized.")
	scopeStack.pop()