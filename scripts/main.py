# -*- encoding: utf-8 -*-
import sys
import numpy
import os, os.path
import random
import codecs
from scripts import *

pref = '/home/last/programming/kursa/progs/'
sys.path.append(pref + 'liga')
sys.path.append(pref + 'langid/langid.py/langid')

import cld2
import liga, liga_original
import langid


def classify(clf, text):
    text = text.encode('utf-8')
    return clf.classify(text)

# monkey-patching cld2 to unify interfaces.
cld2.classify = cld2.detect

def cross_validation(clf, text_folder, percentile=0.6, iterations=6, debug_output=False):
    # perform testing of classifier on .txt files from <text_folder>. 
    # <percentile> of file is going to training set, and the remaining - to test set.
    # Testing is held in-place: /train and /test subfolders are created in <text_folder>,
    # they are deleted after the end of function.

    # Outputs precision and recall of classifier on each iteration as a list of tuples 
    # for each language.
    files = filter(lambda x: x.endswith('.txt') and x != 'russian.txt', os.listdir(text_folder))
    train_folder = text_folder + '/train'
    test_folder = text_folder + '/test'
    for x in [train_folder, test_folder]:
        if not os.path.isdir(x):
            os.mkdir(x)

    results = dict()

    for _ in range(iterations):
        for f in files:
            data = read_data(os.path.join(text_folder, f))
            random.shuffle(data)

            border = int(percentile * len(data))
            train = data[:border]
            test = data[border:]

            write_data(os.path.join(train_folder, f), train)
            write_data(os.path.join(test_folder, f), test)

        # testing and training here

        # initializing classifier and answer converter
        classifier = None
        conv_func = ISO_639_1_map
        if clf == 'liga':
            classifier = liga.LIGA(sep='\n', train_folder=train_folder)
        elif clf == 'liga_original':
            classifier = liga_original.LIGA(sep='\n', train_folder=train_folder)
        elif clf == 'langid':
            classifier = langid
            conv_func = convert_langid_to_str
        elif clf == 'cld2':
            classifier = cld2
            conv_func = convert_cld2_to_str
        else:
            raise ValueError('Unknown classifier!')
        
        # collect answers
        cur_iter = []
        if debug_output:
            debug = './cv_output'   
            debug = open(debug, 'w')
        for f in files:
            data = read_data(os.path.join(test_folder, f))
            for tweet in data:
                predicted = conv_func(classify(classifier, tweet))
                ground_truth = ISO_639_1_map(f[:-4])
                cur_iter.append((ground_truth, predicted))
                if debug_output:
                    debug.write('\n' + ground_truth + ' ' + predicted)
        if debug_output:
            debug.close()

        # evaluate statistics
        languages = numpy.unique([x[0] for x in cur_iter])
        for lang in languages:
            answer_is_lang = filter(lambda x: x[0] == lang, cur_iter)
            predicted_lang = filter(lambda x: x[1] == lang, cur_iter)
            answered_correctly = filter(lambda x: x[0] == x[1] == lang, cur_iter)
             
            if len(predicted_lang) == 0:
                # classifier does not know this language
                continue
            precision = len(answered_correctly) / float((len(predicted_lang)))
            recall = len(answered_correctly) / float(len(answer_is_lang))
            f_measure = 2 * (precision * recall) / (precision + recall)

            results[lang] = results.get(lang, []) + [(precision, recall, f_measure)]

        # end testing

        for f in files:
            os.remove(os.path.join(train_folder, f))
            os.remove(os.path.join(test_folder, f))
    os.rmdir(train_folder)
    os.rmdir(test_folder)
    return results


folder = '/home/last/programming/kursa/parsed_text'
res = cross_validation('cld2', folder, percentile=0.7, iterations=4)
print out_dict(res)
