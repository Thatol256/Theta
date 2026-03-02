import general

def asm(op):
	for o in op.split(";"):
		if o != "": general.asm.append(o.strip())
def wait(): general.asm.append("wai;")

DATATYPES = ["ubyte", "ushort", "uint", "byte", "short", "int", "vector", "pointer", "array"]
REGISTERS = ["A", "X", "Y", "PC"]
ALIASES = {"u8": "ubyte", "u16": "ushort", "u32": "uint", "i8": "byte", "i16": "short", "i32": "int"}

#before translating addressing modes:
#replace variables with their respective address
#replace binary and decimal with hexadecimal
'''
ADDRESSING_MODES = {
	"Immediate": [r"0x([0-9A-Fa-f]{1,4})", r"\\$\\1"],
	"Relative": [r"PC *\+ *0x([0-9A-Fa-f]{1,2})", r"\\$\\1"],
	"Direct": [r"0x([0-9A-Fa-f]{1,2})", r"\\$\\1"],
	"Direct indirect": [r"&2:0x([0-9A-Fa-f]{1,2})", r"\(\\$\\1\)"],
	"Direct indirect long": [r"&3:0x([0-9A-Fa-f]{1,2})", r"\(\\$\\1\)"],
	"Direct X": [r"0x([0-9A-Fa-f]{1,2}) *\+ *X", r"\\$\\1,x"],
	"Direct Y": [r"0x([0-9A-Fa-f]{1,2}) *\+ *Y", r"\\$\\1,y"],
	"Direct inderect X": [r"&2:\(0x([0-9A-Fa-f]{1,2}) *\+ *X *\)", r"\(\\$\\1,x\)"],
	"Direct inderect Y": [r"&2:0x([0-9A-Fa-f]{1,2}) *\+ *Y", r"\(\\$\\1\),y"],
	"Direct inderect long Y": [r"&3:0x([0-9A-Fa-f]{1,2}) *\+ *Y", r"\[\\$\\1\],y"],
	"Absolute": [r"0x([0-9A-Fa-f]{1,4})", r"\\$\\1"],
	"Absolute X": [r"0x([0-9A-Fa-f]{3,4}) *\+ *X", r"\\$\\1,x"],
	"Absolute Y": [r"0x([0-9A-Fa-f]{3,4}) *\+ *Y", r"\\$\\1,y"],
	"Absolute long": [r"0x([0-9A-Fa-f]{5,6})", r"\\$\\1"],
	"Absolute long X": [r"0x([0-9A-Fa-f]{5,6}) *\+ *X", r"\\$\\1,x"],
	"Absolute indirect"
	"Absolute indirect long"
	"Absolute indirect X"
	"Stack relative": [r"0x([0-9A-Fa-f]{1,2}) *\+ *S", r"\\$\\1,s"],
	"Stack relative indirect Y"
}
'''

'''
Absolute indirect: OPC ($0000)           | &2:ADDR
Absolute indirect long: OPC [$0000]      | &3:ADDR
Absolute indirect X: OPC ($0000,x)       | &2:(ADDR + X)
Stack relative indirect Y: OPC ($00,s),y | &2:(ADDR + S) + Y
'''

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
	def push(self): pass
	def pull(self): pass
PC = RegPC()

class RegA (Register):
	def __init__(self): super().__init__("A")
	def __len__(self): pass #depends on pc flag
	def __setattr__(self, x, op):
		if x == "value":
			if isinstance(op, Register):
				match op.name:
					case "X": general.asm.append("txa;")
					case "Y": general.asm.append("tya;")
	def push(self): general.asm.append("pha;")
	def pull(self): general.asm.append("pla;")
	
	def __add__(self, val):
		if isinstance(val, int):
			asm("inc a;" if val==1 else f"adc #{val};")
			return
		
		'''
		ADC (dp,X) 		Add With Carry 	61 	DP Indexed Indirect,X 	NV----ZC 	2 	6[1][2]
		ADC sr,S 		Add With Carry 	63 	Stack Relative 	NV----ZC 	2 	4[1]
		ADC dp 		Add With Carry 	65 	Direct Page 	NV----ZC 	2 	3[1][2]
		ADC [dp] 		Add With Carry 	67 	DP Indirect Long 	NV----ZC 	2 	6[1][2]
		ADC addr 		Add With Carry 	6D 	Absolute 	NV----ZC 	3 	4[1]
		ADC long 		Add With Carry 	6F 	Absolute Long 	NV----ZC 	4 	5[1]
		ADC ( dp),Y 		Add With Carry 	71 	DP Indirect Indexed, Y 	NV----ZC 	2 	5[1][2][3]
		ADC (dp) 		Add With Carry 	72 	DP Indirect 	NV----ZC 	2 	5[1][2]
		ADC (sr,S),Y 		Add With Carry 	73 	SR Indirect Indexed,Y 	NV----ZC 	2 	7[1]
		ADC dp,X 		Add With Carry 	75 	DP Indexed,X 	NV----ZC 	2 	4[1][2]
		ADC [dp],Y 		Add With Carry 	77 	DP Indirect Long Indexed, Y 	NV----ZC 	2 	6[1][2]
		ADC addr,Y 		Add With Carry 	79 	Absolute Indexed,Y 	NV----ZC 	3 	4[1][3]
		ADC addr,X 		Add With Carry 	7D 	Absolute Indexed,X 	NV----ZC 	3 	4[1][3]
		ADC long,X 		Add With Carry 	7F 	Absolute Long Indexed,X 	NV----ZC 	4 	5[1]
		'''
	
	def __radd__(self, val): pass
	def __iadd__(self, val): pass
	def __sub__(self, val): pass
	def __rsub__(self, val): pass
	def __isub__(self, val): pass
	
	def __and__(self, val): pass
	def __rand__(self, val): pass
	def __iand__(self, val): pass
	def __or__(self, val): pass
	def __ror__(self, val): pass
	def __ior__(self, val): pass
	def __xor__(self, val): pass
	def __rxor__(self, val): pass
	def __ixor__(self, val): pass
	
	def __rshift__(self, val): pass
	def __rrshift__(self, val): pass
	def __irshift__(self, val): pass
	def __lshift__(self, val): pass
	def __rlshift__(self, val): pass
	def __ilshift__(self, val): pass
	
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
	def push(self): general.asm.append("phx;")
	def pull(self): general.asm.append("plx;")
	
	def __add__(self, val): pass
	def __radd__(self, val): pass
	def __iadd__(self, val): pass
	def __sub__(self, val): pass
	def __rsub__(self, val): pass
	def __isub__(self, val): pass
	
	def __and__(self, val): pass
	def __rand__(self, val): pass
	def __iand__(self, val): pass
	def __or__(self, val): pass
	def __ror__(self, val): pass
	def __ior__(self, val): pass
	def __xor__(self, val): pass
	def __rxor__(self, val): pass
	def __ixor__(self, val): pass
	
	def __rshift__(self, val): pass
	def __rrshift__(self, val): pass
	def __irshift__(self, val): pass
	def __lshift__(self, val): pass
	def __rlshift__(self, val): pass
	def __ilshift__(self, val): pass
	
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
	def push(self): general.asm.append("phy;")
	def pull(self): general.asm.append("ply;")
	
	def __add__(self, val): pass
	def __radd__(self, val): pass
	def __iadd__(self, val): pass
	def __sub__(self, val): pass
	def __rsub__(self, val): pass
	def __isub__(self, val): pass
	
	def __and__(self, val): pass
	def __rand__(self, val): pass
	def __iand__(self, val): pass
	def __or__(self, val): pass
	def __ror__(self, val): pass
	def __ior__(self, val): pass
	def __xor__(self, val): pass
	def __rxor__(self, val): pass
	def __ixor__(self, val): pass
	
	def __rshift__(self, val): pass
	def __rrshift__(self, val): pass
	def __irshift__(self, val): pass
	def __lshift__(self, val): pass
	def __rlshift__(self, val): pass
	def __ilshift__(self, val): pass
	
	def __eq__(self, val): pass
	def __ne__(self, val): pass
	def __lt__(self, val): pass
	def __gt__(self, val): pass
	def __le__(self, val): pass
	def __ge__(self, val): pass
Y = RegY()

class StoredValue (general.ValueHook):
	# *OBJ -> OBJ.address
	def __init__(self, adr, wid, sig): super().__init__(adr, wid, sig)
	def __len__(self): return super().__len__()
	
	def getBits(self, field): pass
	def getFlag(self, field): pass
	def push(self): pass
	def pull(self): pass
	
	def __add__(self, val): pass
	def __radd__(self, val): pass
	def __iadd__(self, val): pass
	def __sub__(self, val): pass
	def __rsub__(self, val): pass
	def __isub__(self, val): pass
	
	def __and__(self, val): pass
	def __rand__(self, val): pass
	def __iand__(self, val): pass
	def __or__(self, val): pass
	def __ror__(self, val): pass
	def __ior__(self, val): pass
	def __xor__(self, val): pass
	def __rxor__(self, val): pass
	def __ixor__(self, val): pass
	
	def __rshift__(self, val): pass
	def __rrshift__(self, val): pass
	def __irshift__(self, val): pass
	def __lshift__(self, val): pass
	def __rlshift__(self, val): pass
	def __ilshift__(self, val): pass
	
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
	def __init__(self, adr): super().__init__(adr, 1, False)
class ushort (StoredValue):
	def __init__(self, adr): super().__init__(adr, 2, False)
class uint (StoredValue):
	def __init__(self, adr): super().__init__(adr, 4, False)
class byte (StoredValue):
	def __init__(self, adr): super().__init__(adr, 1, True)
class short (StoredValue):
	def __init__(self, adr): super().__init__(adr, 2, True)
class int (StoredValue):
	def __init__(self, adr): super().__init__(adr, 4, True)

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
		self.countStride = StoredValue(self.type.address, countStr, False)
	
	def __getitem__(self, x): pass
	def __setitem__(self, x, val): pass
	def __contains__(self, val): pass

class pointer (general.PointerHook):
	def __init__(self, adr, sval): super().__init__(adr, sval)
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
		self.mode = md
	def __setattr__(self, x, op):
		if x == "value":
			if isinstance(op, Register):
				match op.name:
					case "A": pass
	
	def __add__(self, val): pass
	def __radd__(self, val): pass
	def __iadd__(self, val): pass
	def __sub__(self, val): pass
	def __rsub__(self, val): pass
	def __isub__(self, val): pass
	def __and__(self, val): pass
	def __rand__(self, val): pass
	def __iand__(self, val): pass
	def __or__(self, val): pass
	def __ror__(self, val): pass
	def __ior__(self, val): pass
	def __xor__(self, val): pass
	def __rxor__(self, val): pass
	def __ixor__(self, val): pass
	def __rshift__(self, val): pass
	def __rrshift__(self, val): pass
	def __irshift__(self, val): pass
	def __lshift__(self, val): pass
	def __rlshift__(self, val): pass
	def __ilshift__(self, val): pass
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