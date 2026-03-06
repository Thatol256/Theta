from datetime import datetime
import tonFilesystem as tfs
import subprocess
import general
import re

import traceback

HEADER_CODE = (
"import sys, os\n"
"sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))\n"
)

KEYWORD_FUNCTIONS = ["return"]

def printBar(): print("="*50)
thrown = False
def throw(area, e):
	global thrown
	if not thrown:
		thrown = True
		printBar()
		print(f"{area.upper()} ECOUNTERED AN UN-CAUGHT ERROR:")
		printBar()
		print(e)
		printBar()
		traceback.print_exc()
		printBar()
		input()
		raise Exception()
def catch(area, mess):
	printBar()
	print(f"{area.upper()} CAUGHT AN ERROR:")
	printBar()
	print(mess)
	printBar()
	input()
	raise Exception()

try:
	file = tfs.read("./test.tha")
	file = re.sub(r"\/\/.*", "", file)
	file = re.sub(r"\/\*[\s\S]*\*\/", "", file)
	
	importFiles = []
	imports = {}
	
	# REPLACE FILE IMPORTS
	for u in re.findall(r" *use +.+_.+", file):
		mat = re.search(r" (.+)_(.+)", u)
		fileType = mat.group(1)
		fileName = mat.group(2)
		imports.update({u: f"./{fileType}/{fileType}_{fileName}.py"})
	for i in imports.keys():
		file = file.replace(i, "")
		importFiles.append(tfs.read(imports[i]))
	importFiles = "\n".join(importFiles)
	
	exec(re.search(r"DATATYPES *= *\[[^\]]+\]", importFiles).group())
	exec(re.search(r"ALIASES *= *\{[^\}]+\}", importFiles).group())
	exec(re.search(r"REGISTERS *= *\[[^\]]+\]", importFiles).group())
	
	RE_DATATYPE = r"(?:" + "|".join(DATATYPES) + r")(?:<[!-;A-z]*>)"
	RE_NUMBER = r"(?:%[01]+|0x[\dA-Fa-f]+|\-?\d+(?:\.\d+)?)"
	RE_LABEL = r"\w[\w\d]*"
	
	exec(HEADER_CODE)
	
	# PREPROCESS FUNCTION
	#prMat = re.search(r" *def +PREPROCESS *\( *\) *\: *(?:\n\t+.+)+", file)
	#if prMat != None:
	#	file = file.replace(prMat.group(), "")
	#	rCode = re.sub(r"\n\t", r"\n", prMat.group())
	#	rCode = re.sub(r"[^\n]+\n([\S\s]+)", r"\1", rCode)
	#	exec(rCode)
	
	# POPULATE VARIABLES
	VARIABLES = {}
	for a, v in ALIASES.items(): file = file.replace(a, v)
	RE_NESTEDVAR = re.compile(RE_DATATYPE)
	varDecs = re.findall(RE_DATATYPE + " +" + RE_LABEL + " *(?:= *.+ *)?", file)
	vDecBuffers = []
	for v in varDecs:
		vMat = re.search(f"({RE_DATATYPE}) +" + f"({RE_LABEL}) *" + r"(?:= *(.+) *)?", v)
		vType = vMat.group(1)
		typeCheck = vType if not "<" in vType else vType[:vType.index("<")]
		if not typeCheck in DATATYPES: continue
		vName = vMat.group(2)
		vType = vType.replace("<", f"(\"{vName}\", ").replace(">", ")")
		vContent = vMat.group(3)
		VARIABLES.update({vName: vType})
		vDecBuffers.append(f"{vName} = {vType}\ngeneral.VARIABLES.append({vName})" + ("" if vContent==None else (f"\\n{vName}.value = {vContent}")))
		if vContent != None: file = file.replace(v, f"{v}\n{vName} = {vType}")
	
	# REPLACE SCOPES
	RE_FUNCPREFIX = "(?:(?:void|" + RE_DATATYPE + f") +{RE_LABEL})"
	RE_SCOPEPREFIX = r"(?:(?:do +)?while|for|(?:else +)?if|else|" + RE_FUNCPREFIX + ")"
	RE_SCOPE = re.compile(r"\n\s*" + f"({RE_SCOPEPREFIX})" + r" *\(([^\)\n]*)\) *\{((?:\n(?: {4}|\t)+.*)*?)\n\}")
	scopeMat = RE_SCOPE.search(file)
	while scopeMat != None:
		#input("!!!")
		isFunc = not scopeMat.group(1).replace(" ", "") in ["dowhile", "while", "for", "elseif", "if", "else"]
		scopeType = scopeMat.group(1).replace(" ", "") if not isFunc else scopeMat.group(1).split(" ")
		scopeArgs = scopeMat.group(2) if not isFunc else scopeMat.group(2).split(",")
		scopeCode = scopeMat.group(3).split("\n")
		scopeCode = "\n".join([re.sub(r"(?: {4}|\t)(.*)", r"\1", x) for x in scopeCode])
		scopePrefix = []
		labelStart = general.genId()
		labelEnd = general.genId()
		if scopeType == "for":
			scopeArgs = scopeArgs.split(";")
			scopePrefix.append(scopeArgs[0])
			scopeCode += "\n\t" + scopeArgs[2]
			scopeArgs = scopeArgs[1]
		# TODO: PROCESS CONDITION STATEMENTS
		if scopePrefix == []: scopePrefix = ""
		pScopeType = f"\"{scopeType}\"" if isinstance(scopeType, str) else f"[\"{"\", \"".join(scopeType)}\"]"
		pScopeArgs = f"\"{scopeArgs}\"" if isinstance(scopeArgs, str) else ("[]" if scopeArgs == [""] else f"[\"{"\", \"".join(scopeArgs)}\"]")
		fullCode = f"{scopePrefix}\n{labelStart}:\nscopeStart({pScopeType}, {pScopeArgs}, \"{labelStart}\", \"{labelEnd}\")"
		fullCode += f"\n{scopeCode}\nscopeEnd()\n{labelEnd}:"
		file = file.replace(scopeMat.group(), fullCode)
		scopeMat = RE_SCOPE.search(file)
	
	# HANDLE ASSIGNMENTS (e.g. PC = M -> PC = AddressingMode(M))
	assigns = re.findall(f".+[^=] *(?:[\+\-\*\/]|<<|>>)?= *[^=].+", file)
	for a in assigns:
		aMat = re.search(r"(.+?) *((?:[\+\-\*\/]|<<|>>)?=) *(.+)", a)
		aLeft = " ".join(aMat.group(1).strip().split(" "))
		aAssign = aMat.group(2)
		aRight = " ".join(aMat.group(3).strip().split(" "))
		# TODO: check if aRight contains embedded statements (e.g. A = B == C, A = !B > C)
		if not aLeft in list(VARIABLES.keys()) + REGISTERS: # indirect assignment (VAR1 + X = VAR2 -> LBL = VAR1 + X; LBL = VAR2 )
			aLId = general.genId()
			aLeft = f"{aLId} {aAssign} AddressingMode(\"{aLeft}\")\n{aLId}.value"
		elif aAssign == "=": # variable/register assignment
			aLeft = f"{aLeft}.value"
		if not (aRight in REGISTERS):
			aRight = f"AddressingMode(\"{aRight}\")"
		file = file.replace(a, f"{aLeft} {aAssign} {aRight}", 1)
	
	for i, v in enumerate(varDecs):
		file = file.replace(v, vDecBuffers[i])
		
		# *VAL -> VAL.address
		#  VAL -> &VAL.address
		# *PTR -> PTR.value.address
		#  PTR -> &PTR.value.address
		# &PTR -> &&PTR.value.address
		
		# &(PTR+Y) = A -> STA (PTR.value.address),y
		# &(*VAL+X) = A -> STA VAL.address,x
	
	# REPLACE KEYWORD FUNCTIONS
	kWords = re.findall(r"\n(?:" + "|".join(KEYWORD_FUNCTIONS) + r")\n", file)
	for k in kWords:
		kName = re.search(r"\w+", k).group().capitalize()
		file = file.replace(k, "\nfunc"+kName+"()\n")
	
	# REPLACE LABELS
	for l in re.findall(r" *\w[\w\d]* *:", file):
		lName = re.search(r" *(\w[\w\d]*) *:", l).group(1)
		file = re.sub(l, f"{lName} = general.Label(\"{lName}\")\ngeneral.LABELS.append({lName})", file)
	
	file = "\n".join([importFiles, file])
	
	#print(file)
	try: exec(file)
	except Exception as e: throw("ASSEMBLY MODULE", e)
	#input(general.asm)
	input("TRANSLATION COMPLETE.")
except Exception as e: throw("PRE-PROCESSOR", e)