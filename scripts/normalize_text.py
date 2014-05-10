from string_processing import *
import os, os.path
import sys
import codecs
from scripts import read_data, write_data

#######################################################
# get all .txt files from $1, parse tweets from them
# (should be separated by 'separator') and write to $2 
# with same file name
folder = sys.argv[1]
separator = '\n' + '-' * 60 + '\n' * 4
if not os.path.isdir(sys.argv[2]):
    os.mkdir(sys.argv[2])

for fi in os.listdir(folder):
    if fi.endswith('.txt'):
	texts = read_data(os.path.join(folder, fi), separator)
	parsed = []
        for text in texts:
            text = process(text)
            if text != '':
                parsed.append(text)
        write_data(os.path.join(sys.argv[2], fi), parsed)
