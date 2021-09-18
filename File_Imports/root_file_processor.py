# CURRENTLY NON OPERATIVE - NEEDS UPDATE

#########
#IMPORTS#
#########

from imports.default_imports import *
from imports.functions import * 
from imports.ML_imports import *

import os
import argparse

##################
#ARGUMENT PARSING#
##################

help_text = 'This is the help text.'

# Initialize the parser
parser = argparse.ArgumentParser(description=help_text)

# Add arguments
parser.add_argument('-i', '--input', help='input file path', action='store_true')
#parser.add_argument('-V', '--version', help='show program version', action='store_true')

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
if args.version:
    print('This is myprogram version 1.0')


##########CAN MAKE THIS WHOLE PROCESS A FUNCTION
"""

def parse_args():
  """Handle the command line arguments.

  Returns:
    Output of argparse.ArgumentParser.parse_args.
  """

  parser = argparse.ArgumentParser()
  parser.add_argument('-o', '--output', default='request.json',
                      help='Output file to write encoded images to.')
  parser.add_argument('-r', '--resize', dest='resize', action='store_true',
                      help='Will resize images locally first.  Not needed, but'
                      ' will reduce network traffic.')
  parser.add_argument('inputs', nargs='+', type=argparse.FileType('r'),
                      help='A list of .jpg or .jpeg files to serialize into a '
                      'request json')

  args = parser.parse_args()

  check = lambda filename: filename.lower().endswith(('jpeg', 'jpg'))
  if not all(check(input_file.name) for input_file in args.inputs):
    sys.stderr.write('All inputs must be .jpeg or .jpg')
    sys.exit(1)

  return args 
"""


##################
#DATA PREPARATION#
##################

# get file_path from args
print("args[0]:",args[0])
file_path = args[0]

df = hist_to_df(file_path)
df.to_csv('processed_data.csv')
