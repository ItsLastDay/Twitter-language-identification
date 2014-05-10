import os, os.path
import sys
import codecs

files = os.listdir(sys.argv[1])
for fi in files:
    name = os.path.join(sys.argv[1], fi)
    new_name = fi if '_' not in fi else fi[:fi.index('_')]
    new_name += '.txt'
    new_name = os.path.join(sys.argv[1], new_name)
    fi = codecs.open(name, 'r', 'utf-8')
    data = fi.read()
    fi.close()
    os.remove(name)
    output = codecs.open(new_name, 'w', 'utf-8')
    output.write(data)
    output.close()
