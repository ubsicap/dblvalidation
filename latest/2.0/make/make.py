#!/usr/bin/env python

import sys
import re
import os

if len(sys.argv) != 3:
   print("USAGE: python " + sys.argv[0] + " <inputFilePath> <outputFilePath>")
   sys.exit(1)

inputFilename = sys.argv[1]
outputFilename = sys.argv[2]
fileContents = ""
directory = os.path.dirname(os.path.realpath(__file__))

subRE = re.compile(r"%%insert ([A-Za-z0-9_.-]+)%%")
with open(inputFilename, 'r') as inputFileHandle:
   fileContents = inputFileHandle.read()
   match = re.search(subRE, fileContents)
   while match:
	   insertFilename = match.group(1)
	   print "   " + "inserting " + insertFilename
	   fileContents = re.sub(match.group(0), open(os.path.join(directory, insertFilename), "r").read(), fileContents)
	   match = re.search(subRE, fileContents)

with open(outputFilename, 'w') as outputFileHandle:
   outputFileHandle.write(fileContents)
