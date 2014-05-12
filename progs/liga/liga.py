# -*- coding: utf-8 -*-
import os, codecs, time, argparse, os.path, re, math


_author_ = "Mikhail Koltsov"

class LIGA:
    def __init__(self, sep, model_file=None, train_folder=None, save_to=None):
        ''' Either load model from file or train it on folder.
            Tweets are separated by sep '''
        if (model_file == None) ^ (train_folder == None):
            if model_file != None:
                self.model = LIGA._load_model(model_file)
            else:
                if type(sep) != type('123'):
                    raise ValueError('Tweet separator must be a string')

                self.model = LIGA._train(train_folder, sep)
                if save_to != None:
                    LIGA._dump_model(self.model, save_to)

            self.total_v = sum(self.model[0].values())
            self.total_e = sum(self.model[1].values())
            self.languages = set([x[1] for x in self.model[0].keys()])
            # an improvment to original algorithm:
            # accumulate weights for each language separately
            self.v_by_language = dict()
            self.e_by_language = dict()
            for lang in self.languages:
                self.v_by_language[lang] = 0
                for x in self.model[0].keys():
                    if x[1] == lang:
                        self.v_by_language[lang] += self.model[0][x]
                self.e_by_language[lang] = 0
                for x in self.model[1].keys():
                    if x[2] == lang:
                        self.e_by_language[lang] += self.model[1][x]
        else:
            raise ValueError('You must provide ONE of these: file with model, folder with training set')

    @staticmethod
    def _read_from_file(path, sep):
        ''' returns a list of texts from file
            located at path, tweets are separated by sep '''
        if not os.path.isfile(path):
            raise ValueError('Path provided is not a path to valid file')
        inp = codecs.open(path, 'r', 'utf-8')
        text = inp.read()
        inp.close()
        return filter(lambda x: x != '', text.split(sep))

    @staticmethod
    def _get_ngrams(tweet, n):
        for i in range(len(tweet) - n + 1):
            yield tweet[i:i + n]
    
    @staticmethod
    def _load_model(path):
        ''' Loads model, which was written by _dump_model method,
            which look like 'u'ура', 'russian', 15'''
        if not os.path.isfile(path):
            raise ValueError('Path to model does not refer to a file')
        inp = codecs.open(path, 'r', 'utf-8')
        v = dict()
        e = dict()
        # vexp matches lines like ''' u'ура', 'russian' '''
        vexp = re.compile('''u['"](.+?)['"], ['"](.+?)['"]''')
        n = int(inp.readline())
        for i in range(n):
            kv = inp.readline()
            kv = kv.replace('\n', '')
            match = vexp.search(kv)
            w = int(kv.split(',')[-1][:-1]) # the weight is always last
            trigram = match.group(1)
            trigram = codecs.decode(trigram, 'unicode_escape')
            lang = match.group(2)
            v_key = (trigram, lang)
            v[v_key] = w
        # eexp is much like vexp, but there are two trigrams in line, like:
        # ' u'при', u'рив', 'russian', 10 '
        eexp = re.compile('''u['"](.+?)['"], u['"](.+?)['"], ['"](.+?)['"]''')
        m = int(inp.readline())
        for i in range(m):
            kv = inp.readline()
            kv = kv.replace('\n', '')
            w = int(kv.split(',')[-1][:-1])
            match = eexp.search(kv)
            prev = match.group(1)
            trigram = match.group(2)
            lang = match.group(3)
            e_key = (prev, trigram, lang)
            e[e_key] = w
        return (v, e)

    @staticmethod
    def _dump_model(m, path):
        ''' writes a model (two dicts: vertices and edges) in form:
            len(dict)
            (key1, value1)
            (key2, value2)
            ...
            (key<len(dict)>, value<len(dict)>.
            Keys are written to output in parenthesis by python.'''
        output = codecs.open(path, 'w', 'utf-8')
        v, e = m

        output.write(str(len(v)) + '\n')
        output.write('\n'.join(map(str, ([(key, v[key]) for key in v.keys()]))))

        output.write('\n' + str(len(e)) + '\n')
        output.write('\n'.join(map(str, ([(key, e[key]) for key in e.keys()]))))

        output.close()

    @staticmethod
    def _train(train_folder, sep):
        ''' considers every file <lang>.txt as a part
            of the training set. Builds a model from all such files
            in folder. Notice that language is derived from filename.
            returns two dicts: 
                vertices: (trigram, lang) -> weight
                edges: (prev_trigram, trigram, lang) -> weight'''
        if not os.path.isdir(train_folder):
            raise ValueError('Path does not refer to valid folder')
        vertices = dict()
        edges = dict()

        langs = sorted(filter(lambda x: x[-3:] == 'txt', os.listdir(train_folder)))
        for lang in langs:
            tweets = LIGA._read_from_file(os.path.join(train_folder, lang), sep)
            lang = lang.replace('.txt', '')
            for tweet in tweets:
                prev_trigram = None
                for trigram in LIGA._get_ngrams(tweet, 3):
                    v_key = (trigram, lang)
                    vertices[v_key] = vertices.get(v_key, 0) + 1
                    if prev_trigram != None:
                        e_key = (prev_trigram, trigram, lang)
                        edges[e_key] = edges.get(e_key, 0) + 1
                    prev_trigram = trigram
        return (vertices, edges)
    
    @staticmethod
    def _normalize_score(scores):
        # make the sum of scores equal to 1 
        r = sum(scores.values())
        if r == 0:
            return scores

        for key in scores.keys():
            scores[key] = scores[key] / r
        return scores
    
    @staticmethod
    def _get_best(scores):
        # returns key corresponding to highest value
        r = max(scores.values())
        for key in scores.keys():
            if scores[key] == r:
                return key
        return None

    def _walk(self, text):
        ''' walk in model (graph) based on <text>,
            compute score for every language meant by model'''
        prev = None
        scores = dict()

        # convert to utf
        if isinstance(text, str):
            text = text.decode('utf-8')

        for lang in self.languages:
            scores[lang] = 0.0

        langs_count = len(self.languages)
        for trig in LIGA._get_ngrams(text, 3):
            amp_vertex = len([x for x in self.languages if (trig, x) in self.model[0]])
            amp_vertex = math.log(langs_count / float(amp_vertex) if amp_vertex else 1) + 1

            amp_edge = len([x for x in self.languages if (prev, trig, lang) in self.model[1]])
            amp_edge = math.log(langs_count / float(amp_edge) if amp_edge else 1) + 1
            for lang in self.languages:
                v_key = (trig, lang)
                # add score for the vertex corresponding to <trig>
                scores[lang] += amp_vertex * (self.model[0].get(v_key, 0) * 1.0) / \
                        self.v_by_language[lang] * amp_vertex
                # if there were trigram before, add score of an edge
                # (<prev>, <trig>)
                if prev != None:
                    e_key = (prev, trig, lang)
                    scores[lang] += (self.model[1].get(e_key, 0) * 1.0) / \
                            self.e_by_language[lang] * amp_edge
            prev = trig

        return scores

    def classify_file(self, sep, path):
        ''' Return a list, where for every tweet from a file located on path and separated by sep:
            the predicted language'''
        if not os.path.isfile(path):
            raise ValueError('Path does not point to a valid file')
        tweets = LIGA._read_from_file(path, sep)
        res = []
        for tweet in tweets:
            scores = self._walk(tweet)
            scores = LIGA._normalize_score(scores)
            res.append(LIGA._get_best(scores))
        return res

    def classify(self, text):
        scores = self._walk(text)
        scores = LIGA._normalize_score(scores)
        answer = LIGA._get_best(scores)
        return answer
            


