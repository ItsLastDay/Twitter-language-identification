import liblinearutil
import math
import string
import os, os.path
import codecs
import urllib
from urlparse import urlparse

class LogR:
    def __init__(self, folder):
        self.ngrams = dict()
        self.domains = dict()
        self.names = dict()
        self.hosts = dict()
        self.protocols = dict()
        self.hashtags = dict()
        self.mentions = dict()
        self.locations = dict()
        self.languages = dict()
        self.model = None
        self._train(folder)

    @staticmethod
    def _read_from_file(f):
        # reads train info from file
        f = codecs.open(f, 'r', 'utf-8')
        data = f.read().split('\n')
        f.close()
        return data

    @staticmethod
    def _get_dict_and_update(d, key):
        # if key is not present in dictionary, assign value len(d) to it.
        # Otherwise, return value for that key.
        if key not in d:
            d[key] = len(d)
        return d[key]

    @staticmethod
    def _is_latin(s):
        if s == 'not-given':
            return 0
        for i in s:
            if i.isalpha() and i not in string.letters:
                return 0
        return 1

    def _extract_features(self, tweet):
        # use 'sparse data' notation for liblinear
        cur = dict() 
        text, uname, sname, loc, htags, mentions, links = tweet.split('\t') 

        # separate features from each other
        shift = 0

        # features for user name
        for i in range(1, len(uname)):
            cur[shift + i] = LogR._get_dict_and_update(self.names, uname[:i])
        shift += 50 # 50 chars for uname

        # features for screen name
        for i in range(1, len(sname)):
            cur[shift + i] = LogR._get_dict_and_update(self.names, sname[:i])
        shift += 50 # 50 chars for sname

        # features for location
        cur[shift] = LogR._get_dict_and_update(self.locations, loc)
        shift += 1

        # features for latin script
        cur[shift] = LogR._is_latin(loc)
        cur[shift + 1] = LogR._is_latin(uname)
        shift += 2

        # features for hashtags
        for i, tag in enumerate(htags):
            cur[shift + i] = LogR._get_dict_and_update(self.hashtags, tag)
        shift += 10 # 10 hashtags max

        # features for mentions
        for i, mention in enumerate(mentions):
            cur[shift + i] = LogR._get_dict_and_update(self.mentions, mention)
        shift += 15 # 15 mentions max

        # features for links
        for i, link in enumerate(links):
            try:
                resp = urllib.urlopen(link)
                link = resp.url
            except:
                continue
            parts = urlparse(link)
            body = parts.netloc
            if '/' in body:
                body = body[:body.find('/')]
            first_dot = body.rfind('.')
            second_dot = body.rfind('.', first_dot - 1)
            cur[shift + 3 * i] = LogR._get_dict_and_update(self.domains, \
                body[first_dot + 1:])
            cur[shift + 3 * i + 1] = LogR._get_dict_and_update(self.protocols, \
                    parts.scheme)
            cur[shift + 3 * i + 2] = LogR._get_dict_and_update(self.hosts, \
                    body[second_dot + 1:first_dot])
        shift += 5 # 5 links max
        
        # features for ngrams
        for start in range(len(text)):
            for length in range(1, 5):
                if start + length > len(text):
                    break
                ngram = text[start:start + length]
                cur[shift + LogR._get_dict_and_update(self.ngrams, ngram)] = \
                        1 + math.log(text.count(ngram))

        return cur

    def _train(self, folder):
        # train classifier on all .txt files in <folder>
        entities = dict()
    
        files = filter(lambda x: x.endswith('.txt'), os.listdir(folder))
        for f in files:
            # assign number to current language
            print 'LogR adds file ' + f
            for tweet in LogR._read_from_file(os.path.join(folder, f)):
                # get features
                features = self._extract_features(tweet)
                # push out twit into training set
                ind = LogR._get_dict_and_update(self.languages, f[:-4])
                entities[ind] = entities.get(ind, []) + [features]

        target = []
        objects = []
        for lang in entities.keys():
            for obj in entities[lang]:
                target.append(lang)
                objects.append(obj)
        
        print 'LogR started training...'
        self.model = liblinearutil.train(target, objects, '-s 0')
        print 'Finished!'

    def classify(self, tweet):
        features = self._extract_features(tweet)
        value = liblinearutil.predict([0], [features], self.model)[0][0]
        for lang, number in self.languages.items():
            if number == value:
                return lang
        raise ValueError




