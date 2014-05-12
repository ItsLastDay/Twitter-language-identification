# -*- encoding: utf-8 -*-
import sys
import numpy
import os, os.path
import random
import codecs
from subprocess import call
from scripts import *

pref = '/home/last/programming/kursa/progs/'
sys.path.append(pref + 'liga')
sys.path.append(pref + 'logr')
sys.path.append(pref + 'langid/langid.py/langid')

import logr
import cld2
import textcat
from textcat import ShortException, UnknownException
import liga, liga_original
import langid


def classify(clf, text):
    text = text.encode('utf-8')
    try:
        return clf.classify(text)
    except (UnknownException, ShortException):
        return 'unkown'

# monkey-patching cld2 to unify interfaces.
cld2.classify = cld2.detect

def cross_validation(clf, text_folder, percentile=0.6, iterations=6, debug_output=False, dbg_file='cv_output'):
    # perform testing of classifier on .txt files from <text_folder>. 
    # <percentile> of file is going to training set, and the remaining - to test set.
    # Testing is held in-place: /train and /test subfolders are created in <text_folder>,
    # they are deleted after the end of function.

    # Outputs precision and recall of classifier on each iteration as a list of tuples 
    # for each language.
    files = filter(lambda x: x.endswith('.txt'), os.listdir(text_folder))
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
            
            # make textcat "fingerprints"
            if clf == 'textcat':
                call(["createfp"], \
                    stdin=codecs.open(os.path.join(train_folder, f), 'r', 'utf-8'), \
                    stdout=codecs.open(os.path.join(train_folder, f + '.lm'), 'w', 'utf-8'))
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
        elif clf == 'logr':
            classifier = logr.LogR(train_folder)            
        elif clf == 'textcat':
            # textcat is not that easy to train
            conf = open(os.path.join(train_folder, 'config'), 'w')
            for f in files:
                conf.write(os.path.join(train_folder, f + '.lm') + ' ' + f[:-4] + '\n')
            conf.close()
            classifier = textcat.TextCat(os.path.join(train_folder, 'config'))
            conv_func = convert_textcat_to_str
        else:
            raise ValueError('Unknown classifier!')
            
        # collect answers
        cur_iter = []
        if debug_output:
            debug = codecs.open(dbg_file, 'w', 'utf-8')
        print 'Iteration ', _, 'for classifier', clf
        for f in files:
            data = read_data(os.path.join(test_folder, f))
            print 'Getting answers for ' + f[:-4] + '...'
            for tweet in data:
                predicted = conv_func(classify(classifier, tweet))
                ground_truth = ISO_639_1_map(f[:-4])
                cur_iter.append((ground_truth, predicted))
                if debug_output and _ == iterations - 1 and ground_truth != predicted:
                    debug.write(ground_truth + ' ' + predicted + '        ' + tweet + '\n')
        if debug_output:
            debug.close()

        # evaluate statistics
        print 'Evaluating statistics...'
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
            f_measure = 2 * (precision * recall) / (precision + recall) if precision + recall else 0

            results[lang] = results.get(lang, []) + [(precision, recall, f_measure)]

        # end testing

        for f in files:
            os.remove(os.path.join(train_folder, f))
            os.remove(os.path.join(test_folder, f))
            if clf == 'textcat':
                os.remove(os.path.join(train_folder, f + '.lm'))
        if clf == 'textcat':
            os.remove(os.path.join(train_folder, 'config'))
    os.rmdir(train_folder)
    os.rmdir(test_folder)
    return results


folder = '/home/last/programming/kursa/parsed_text'
'''for clf in ['liga']:# ['textcat', 'liga', 'liga_original', 'cld2', 'langid']:
    for percentile in [0.7, 0.8]:
        output_file = clf + '_' + str(percentile)
        res = cross_validation(clf, folder, percentile=percentile, \
                iterations=10, debug_output=True, dbg_file=output_file + '_dump')
        nice = out_dict(res)
        write_data(output_file, [nice])
'''
clf = liga.LIGA(sep='\n', train_folder=folder)
ans = clf.classify_file('\n', folder + '/farsi.txt')
for x in ans:
    print x
