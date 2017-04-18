#!/usr/bin/env python

import argparse
import getpass
import os
import platform
import re
import sys
import time

# Check cli args

parser = argparse.ArgumentParser(description="Assemble RelaxNG compact schema from components")
parser.add_argument("input", type=str, help="input file")
parser.add_argument("output", type=str, help="output file")
parser.add_argument("--mode", dest="mode", help="mode (strict, lax or something else, eg upload)", action="store")
parser.add_argument("--verbose", dest="verbose", help="verbose", action="store_true")
parser.add_argument("--quiet", dest="verbose", help="quiet", action="store_false")
parser.set_defaults(mode="strict", verbose=True)
args = parser.parse_args()

inputFilename = args.input
outputFilename = args.output
mode = args.mode
verbose = args.verbose
fileContents = ""
directory = os.path.dirname(inputFilename)

# Do repeated substitution, avoiding duplicates
inserted = {}
subRE = re.compile(r"%%insert ([A-Za-z0-9_.-]+)%%")
with open(inputFilename, 'r') as inputFileHandle:
   fileContents = inputFileHandle.read()
   match = re.search(subRE, fileContents)
   while match:
      insertFilename = match.group(1)
      if insertFilename in inserted:
         if verbose:
            print "   " + "skipping " + insertFilename + " (already inserted)"
         fileContents = re.sub(match.group(0), "", fileContents, count=1)
      else:
         inserted[insertFilename] = True
         if mode == "lax":
            insertFilename = re.sub("_text_", "_lax_text_", insertFilename)
         elif mode != "strict" and os.path.exists(os.path.join(directory, re.sub("_rnc", "_{0}_rnc".format(mode), insertFilename))):
               insertFilename = re.sub("_rnc", "_{0}_rnc".format(mode), insertFilename)
         insertFilePath = os.path.join(directory, insertFilename)
         if not(os.path.exists(insertFilePath)):
            print("ERROR: could not find file '{0}' during insert".format(insertFilePath))
            sys.exit(1)
         if verbose:   
            print "   " + "inserting " + insertFilename
         fileContents = re.sub(match.group(0), open(insertFilePath, "r").read(), fileContents, count=1)
      match = re.search(subRE, fileContents)

# Add header
header = "# {0} v{1}\n# Generated by {2}@{3} using makeRNC.py\n# Generated {4}\n\n".format(
   os.path.basename(outputFilename),
   re.sub("_", ".", os.path.abspath(outputFilename).split("/")[-3]),
   getpass.getuser(),
   platform.node(),
   time.strftime("%c")
   )
fileContents = header + fileContents      

# Tidy whitespace
fileContents = re.sub(" +\n", "\n", fileContents)
fileContents = re.sub("\n( *\n)+", "\n\n", fileContents)

# Write out completed schema
with open(outputFilename, 'w') as outputFileHandle:
   outputFileHandle.write(fileContents)
