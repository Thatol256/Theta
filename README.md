# Theta

I have always wanted to create an SNES game in order to test my knowledge of the hardware. However, there were a couple of obsticals in my way:
1. Programming in raw Assembly is slow and painful.
2. Programming in other languages usually require the use of libraries, and with my luck, I am always unable to get it to work.

So, here is a project that solves both problems.

Theta is a programming language that will easily allow you to generate Assembly code for any Assembly language, and does not require any dependencies, libraries, or installations other than the Python programming language. The language works by converting Theta code into Python code. After that, an Assembly module is introduced, and overrides Python's functionality to generate Assembly code rather than actually executing Python code. An Assembly module is a script made specifically for a specific Assembly language, and the Pre-Processor script simplifies code as much as possible, so the creation of an Assembly module requires minimal effort.

## Current Progress
- The Pre-processor is complete, although there is still minimal error checking.
- The goal of this project wasn't to impliment every planned feature, but rather to impliment enough of them to translate a sample Theta file, so although not everything is complete, it is considered done.
- Some features that have not been implimented yet: If statements, pointers, for loops, arrays.
- An example of Theta code is present in the "example" folder, alongside an Assembly file the Theta code is trying to mimic.
- The Assembly code that will be generated from this program should function similarly to that file.

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
- Open the "main.py" script and put in the input and output files, or you can run the script on the command line with "main.py INPUT_FILE -o OUTPUT_FILE"

