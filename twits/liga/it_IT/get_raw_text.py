import os, codecs

files = filter(lambda x: x[-3:] == 'txt', os.listdir(os.getcwd()))
output = codecs.open('output', 'w', 'utf-8')
for f in files:
    inp = codecs.open('./' + f, 'r', 'utf-8')
    text = inp.read()
    output.write('\n' + '-' * 60 + '\n' * 4 + text)
    inp.close()

output.close()
