import datetime

asm = []

VARIABLES = []
LABELS = []

ERROR_FUNCNDEF = "Function is not defined."

def addAsm(op):
	if isinstance(op, list): op = ";".join(op)
	for o in op.split(";"):
		if o != "": asm.append(o.strip())
def addRaw(txt):
	if isinstance(txt, list): txt = "\n".join(txt)
	for o in txt.split("\n"):
		if o != "": asm.append(o.strip())

def printBar(): print("="*50)
def catch(area, mess): # mess is short for message but i guess the word mess works in this context too
	printBar()
	print(f"{area.upper()} CAUGHT AN ERROR:")
	printBar()
	print(mess)
	printBar()
	input()
	raise Exception()

#YYYYYYYY YYYYYYYY YYMMMMDD DDDHHHHH NNNNNNSS SSSSCCCC CCCCCCCC CCCCCCCC
def genId():
	now = datetime.datetime.now()
	h1 = bin(now.year)[2:].rjust(18,"0") + bin(now.month)[2:].rjust(4,"0") + bin(now.day)[2:].rjust(5,"0") + bin(now.hour)[2:].rjust(5,"0")
	h2 = bin(now.minute)[2:].rjust(6,"0") + bin(now.second)[2:].rjust(6,"0") + bin(now.microsecond)[2:].rjust(20,"0")
	res = hex(int(h1+h2, 2))[2:].upper()
	return "ID_"+res

class Register:
	def __init__(self, n, w):
		self.name = n
		self.using = False
		self.pushes = 0
		self.width = w
	def __str__(self): return self.name
	
	def push(self): catch("REGISTER.PUSH()", ERROR_FUNCNDEF)
	def pull(self): catch("REGISTER.PULL()", ERROR_FUNCNDEF)
	
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
	
	def __add__(self, val): catch("REGISTER.__ADD__()", ERROR_FUNCNDEF)
	def __radd__(self, val): catch("REGISTER.__RADD__()", ERROR_FUNCNDEF)
	def __iadd__(self, val): catch("REGISTER.__IADD__()", ERROR_FUNCNDEF)
	def __sub__(self, val): catch("REGISTER.__SUB__()", ERROR_FUNCNDEF)
	def __rsub__(self, val): catch("REGISTER.__RSUB__()", ERROR_FUNCNDEF)
	def __isub__(self, val): catch("REGISTER.__ISUB__()", ERROR_FUNCNDEF)
	def __mul__(self, val): catch("REGISTER.__MUL__()", ERROR_FUNCNDEF)
	def __rmul__(self, val): catch("REGISTER.__RMUL__()", ERROR_FUNCNDEF)
	def __imul__(self, val): catch("REGISTER.__IMUL__()", ERROR_FUNCNDEF)
	def __truediv__(self, val): catch("REGISTER.__TRUEDIV__()", ERROR_FUNCNDEF)
	def __rtruediv__(self, val): catch("REGISTER.__RTRUEDIV__()", ERROR_FUNCNDEF)
	def __itruediv__(self, val): catch("REGISTER.__ITRUEDIV__()", ERROR_FUNCNDEF)
	def __floordiv__(self, val): catch("REGISTER.__FLOORDIV__()", ERROR_FUNCNDEF)
	def __rfloordiv__(self, val): catch("REGISTER.__RFLOORDIV__()", ERROR_FUNCNDEF)
	def __ifloordiv__(self, val): catch("REGISTER.__IFLOORDIV__()", ERROR_FUNCNDEF)
	def __and__(self, val): catch("REGISTER.__AND__()", ERROR_FUNCNDEF)
	def __rand__(self, val): catch("REGISTER.__RAND__()", ERROR_FUNCNDEF)
	def __iand__(self, val): catch("REGISTER.__IAND__()", ERROR_FUNCNDEF)
	def __or__(self, val): catch("REGISTER.__OR__()", ERROR_FUNCNDEF)
	def __ror__(self, val): catch("REGISTER.__ROR__()", ERROR_FUNCNDEF)
	def __ior__(self, val): catch("REGISTER.__IOR__()", ERROR_FUNCNDEF)
	def __xor__(self, val): catch("REGISTER.__XOR__()", ERROR_FUNCNDEF)
	def __rxor__(self, val): catch("REGISTER.__RXOR__()", ERROR_FUNCNDEF)
	def __ixor__(self, val): catch("REGISTER.__IXOR__()", ERROR_FUNCNDEF)
	def __rshift__(self, val): catch("REGISTER.__RSHIFT__()", ERROR_FUNCNDEF)
	def __rrshift__(self, val): catch("REGISTER.__RRSHIFT__()", ERROR_FUNCNDEF)
	def __irshift__(self, val): catch("REGISTER.__IRSHIFT__()", ERROR_FUNCNDEF)
	def __lshift__(self, val): catch("REGISTER.__LSHIFT__()", ERROR_FUNCNDEF)
	def __rlshift__(self, val): catch("REGISTER.__RLSHIFT__()", ERROR_FUNCNDEF)
	def __ilshift__(self, val): catch("REGISTER.__ILSHIFT__()", ERROR_FUNCNDEF)
	def __eq__(self, val): catch("REGISTER.__EQ__()", ERROR_FUNCNDEF)
	def __ne__(self, val): catch("REGISTER.__NE__()", ERROR_FUNCNDEF)
	def __lt__(self, val): catch("REGISTER.__LT__()", ERROR_FUNCNDEF)
	def __gt__(self, val): catch("REGISTER.__GT__()", ERROR_FUNCNDEF)
	def __le__(self, val): catch("REGISTER.__LE__()", ERROR_FUNCNDEF)
	def __ge__(self, val): catch("REGISTER.__GE__()", ERROR_FUNCNDEF)

class ValueHook:
	def __init__(self, nam, adr, wid, sig):
		self.name = nam
		self.address = adr
		self.width = wid
		self.sign = sig
	def __len__(self): return self.wid
	def replaceSymbol(syntax): return "0x"+hex(self.address)[2:]

class PointerHook (ValueHook):
	def __init__(self, nam, adr, sval):
		wid = (math.floor(math.log2(adr)) if adr > 1 else 1) // 8
		super().__init__(nam, adr, wid, False)
		self.reference = sval #the value the pointer points to
	def __len__(self): return self.wid

class Label:
	def __init__(self, nam):
		self.name = nam
		asm.append(nam + ":")

#pointer(0x0123, pointer(0x4567, u16(0x89AB)))
