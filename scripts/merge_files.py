import os, os.path
import sys
import codecs

############################################################
# merges contents of files with common prefix >= $2
# located in folder $1

def read_from_file(fname):
    fname = codecs.open(fname, 'r', 'utf-8')
    data = fname.read()
    fname.close()
    return data

def lcp(s1, s2):
    # largest common prefix
    if len(s1) < len(s2):
        s1, s2 = s2, s1
    ans = len(s2)
    while not s1.startswith(s2[:ans]):
        ans -= 1
    if s2[ans - 1] == '_':
        ans -= 1
    return s2[:ans]

files = os.listdir(sys.argv[1])
files = sorted(files)
long_enough = int(sys.argv[2]) # be afraid of not to loose everything in case of misuse
for i in range(len(files) - 1):
    if files[i + 1].startswith(files[i][:long_enough]):
        common = lcp(files[i], files[i + 1])
        print 'Merging ', files[i + 1], files[i], 'into', common
        name1 = os.path.join(sys.argv[1], files[i])
        name2 = os.path.join(sys.argv[1], files[i + 1])
        data1 = read_from_file(name1)
        data2 = read_from_file(name2)
        os.remove(name1)
        os.remove(name2)
        merged = codecs.open(os.path.join(sys.argv[1], common), 'w', 'utf-8')
        merged.write(data1)
        merged.write(data2)
        files[i + 1] = common
        merged.close()
