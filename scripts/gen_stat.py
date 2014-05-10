import os, os.path
import codecs
import sys

####################################################################
# counts tweets in every .txt file in folder $1
# separated by '\n' (should be the case after text normalizing).


langs = filter(lambda s: s[-3:] == 'txt', os.listdir(sys.argv[1]))
langs = sorted(langs)
output = open(os.path.join(sys.argv[1], "STATISTICS"), "w")
total = 0
for lang in langs:
    inp = codecs.open(os.path.join(sys.argv[1], lang), "r", "utf-8").read()
    twits = inp.count('\n')
    output.write(lang[:-4] + ": " + str(twits) + '\n')
    total += twits
output.write('-' * 60 + '\n' + "TOTAL: " + str(total))
output.close()
