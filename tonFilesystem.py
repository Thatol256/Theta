import shutil
import os
import re

RBC = r"\\\/:\*\?\"<>\|"
REGEX_PATH = re.compile(fr"^(?:([A-Z]:|\.*)[\\\/])?((?:[^{RBC}]+[\\\/])*)(?:([^{RBC}]+)(\.[^{RBC}]+)?)?$")

def isValid(pat): return pat != "" and REGEX_PATH.search(pat) != None

def getParts(pat):
	if not isinstance(pat, str): raise TypeError("Path must be a string.")
	if pat == "": raise ValueError("Path cannot be empty.")
	mat = REGEX_PATH.search(pat)
	if mat == None: raise ValueError(f"Path ({pat}) is not valid.")
	return mat.group(1), mat.group(2), mat.group(3), mat.group(4) #drive, directory, filename, extension

def isFile(pat): return pat != "" and not pat[-1] in ["\\", "/"]
def isDirectory(pat): return pat != "" and pat[-1] in ["\\", "/"]
def isFolder(pat): return isDirectory(pat)

REGEX_IS_ABSOLUTE = re.compile(r"^[A-Z]:")
def isRelative(pat): return pat != "" and REGEX_IS_ABSOLUTE.search(pat) == None
def isAbsolute(pat): return pat != "" and not isRelative(pat)

def toRelative(pat): pass
def toAbsolute(pat): pass

def exists(pat): return os.path.exists(pat)

def unpackFolder(pat):
	fs = []
	for root, dirs, files in os.walk(pat):
		for file in files: fs.append(os.path.join(root, file))
	return fs

def prompt(message, **kwargs):
	allowMultiple = kwargs.get("allowMultiple", False)
	allowFile = kwargs.get("allowFile", True)
	allowFolder = kwargs.get("allowFolder", False)
	allowRelative = kwargs.get("allowRelative", True)
	allowAbsolute = kwargs.get("allowAbsolute", True)
	unpackFolders = kwargs.get("unpackFolders", False)
	mustExist = kwargs.get("mustExist", True)
	objs = []
	
	inputValid = False
	while not inputValid:
		ans = ",".join(input(message).split(",")).split(",")
		ans = [a.strip() for a in ans]
		inputValid = True
		if len(ans) > 1 and not allowMultiple: inputValid = False; continue
		for object in ans:
			if isValid(object): inputValid = False; continue
			if mustExist and not exists(object): inputValid = False; continue
			if not allowFile and isFile(object): inputValid = False; continue
			if not allowFolder and isFolder(object): inputValid = False; continue
			if not allowRelative and isRelative(object): inputValid = False; continue
			if not allowAbsolute and isAbsolute(object): inputValid = False; continue
			if isFolder(object): objs += unpackFolder(object)
			else: objs.append(object)
	return objs

def delete(pat): os.remove(pat)
def shred(pat, passes=10):
	with open(pat, 'wb+') as file:
		file.seek(0, os.SEEK_END)
		length = file.tell()
		for _ in range(passes):
			file.seek(0)
			file.write(os.urandom(length))
	delete(pat)

def rename(old, new): os.rename(old, new)
def move(old, new): shutil.move(old, new)
def copy(old, new):
	if isFile(old) and isFile(new): shutil.copy(old, new)
	elif isFolder(old) and isFolder(new): shutil.copytree(old, new)
def create(pat):
	if isFile(pat):
		with open(pat, "x") as f: pass
	elif isFolder(pat): os.mkdir(pat)

def read(pat, binary=False):
	data = None
	with open(pat, "r" if not binary else "rb") as file:
		data = file.read()
	return data
def append(pat, data, binary=False):
	with open(pat, "a" if not binary else "ab") as file:
		file.write(data)
def write(pat, data, binary=False):
	with open(pat, "w" if not binary else "wb") as file:
		file.write(data)