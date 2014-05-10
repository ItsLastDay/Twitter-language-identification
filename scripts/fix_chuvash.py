# -*- encoding: utf-8 -*-
import os, os.path
import codecs
import sys
from scripts import read_data, write_data

# My chuvash tweets are derived from one user - ChuvashOrg
# and contain tokens that may distinguish them from others,
# namely, they mostly start with 'Хыпар' and end with 'via @ChuvashOrg'.

sep = '\n' + '-' * 60 + '\n' * 4  

data = read_data(sys.argv[1])

new_data = []
for tweet in data:
    if not tweet.startswith(u'Хыпар'):
        continue
    tweet = tweet.replace(u'Хыпар', '')
    tweet = tweet.replace(u'via @ChuvashOrg', '')
    new_data.append(tweet)

write_data(sys.argv[1], new_data, sep)
