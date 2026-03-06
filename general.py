import datetime

asm = []

VARIABLES = []
LABELS = []

#YYYYYYYY YYYYYYYY YYMMMMDD DDDHHHHH NNNNNNSS SSSSCCCC CCCCCCCC CCCCCCCC
def genId():
	now = datetime.datetime.now()
	h1 = bin(now.year)[2:].rjust(18,"0") + bin(now.month)[2:].rjust(4,"0") + bin(now.day)[2:].rjust(5,"0") + bin(now.hour)[2:].rjust(5,"0")
	h2 = bin(now.minute)[2:].rjust(6,"0") + bin(now.second)[2:].rjust(6,"0") + bin(now.microsecond)[2:].rjust(20,"0")
	res = hex(int(h1+h2, 2))[2:].upper()
	return "ID_"+res

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
