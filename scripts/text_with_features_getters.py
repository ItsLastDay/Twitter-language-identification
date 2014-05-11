# -*- coding: utf-8 -*-
import os, os.path
import json
import codecs
import nltk
import sys
from scripts import read_data, write_data
from string_processing import *

''' The general difference between this file and plain_text_getters is that
    scripts here output text with features for logr classifier. It look like:
    text\tuser_name\tscreen_name\tlocation\thashtag1,hashtag2, ...\tmention1,
    mention2, ...\tlink1,link2, ...
    Another difference is that the processing (normalization) goes here.
'''

def bergsma_get_text(inp, output):
    # extract text with features from tweet in format provided by
    # Shane Bergsma from paper 
    # 'Language Identification for Creating Language-Specific Twitter Collections'.
    data = read_data(inp)

    res = []
    for line in data:
        tokens = line.split('\t')
        if len(tokens) < 3:
            continue

        text = tokens[5]
        mentions = get_mentions(text)
        links = get_links(text)
        hashtags = get_hashtags(text)
        text = process(text)
        sname = tokens[1]
        uname = tokens[2]
        location = tokens[3]
        row = [text, uname, sname, location, ','.join(hashtags), ','.join(mentions), ','.join(links)]
        row = '\t'.join(row)
        if text == '':
            continue
        
        res.append(row)
    
    write_data(output, res)


def plain_get_text(folder, output, prefix=''):
    # writes text with features from every file in <folder> starting with 
    # <prefix> to <output>. 
    files = filter(lambda x: x.startswith(prefix), os.listdir(folder))
    separator = '\n' + '-' * 60 + '\n' * 4
    out_data = []
    for fi in files:
        fi = codecs.open(os.path.join(folder, fi), 'r', 'utf-8')
        out = fi.read()
        fi.close()
        
        out = process(out)
        if out == '':
            continue
        out = [out] + ['not-given', 'not-given', 'not-given', '', '', '']
        out = '\t'.join(out)

        out_data.append(out)

    write_data(output, out_data)

def russian_get_text(inp, output):
    # parse tweets from .csv file by Julia Rubtsova
    # from 'Метод построения и анализа корпуса коротких текстов для задачи классификации отзывов'
    data = read_data(inp)

    res = []
    pattern = '''"(.*?)";'''
    for line in data:
        tokens = nltk.regexp_tokenize(line, pattern)
        if len(tokens) < 4:
            continue

        text = tokens[3][1:-2]
        mentions = get_mentions(text)
        links = get_links(text)
        hashtags = get_hashtags(text)
        text = process(text)
        sname = tokens[2][1:-2]
        if text == '':
            continue

        row = [text, 'not-given', sname, 'not-given', ','.join(hashtags), ','.join(mentions), ','.join(links)]
        row = '\t'.join(row)

        res.append(row)

    write_data(output, res)

def json_get_text(folder, output, prefix=''):
    # writes json text from every file in <folder> starting with 
    # <prefix> to <output>. 
    files = filter(lambda x: x.startswith(prefix), os.listdir(folder))
    out_data = []
    for fi in files:
        fi = codecs.open(os.path.join(folder, fi), 'r', 'utf-8')

        out = json.load(fi)
        
        text = out[u'text']
        mentions = get_mentions(text)
        links = get_links(text)
        hashtags = get_hashtags(text)
        text = process(text)
        if text == '':
            continue 

        sname = out[u'user'][u'screen_name']
        try:
            uname = out[u'user'][u'name']
        except KeyError:
            uname = 'not-given'
        try:
            location = out[u'user'][u'location']
        except KeyError:
            location = 'not-given'
        row = [text, uname, sname, location, ','.join(hashtags), ','.join(mentions), ','.join(links)]
        row = '\t'.join(row)

        out_data.append(row)
        fi.close()
    
    write_data(output, out_data)

func = bergsma_get_text
if sys.argv[1] == '1':
    func = plain_get_text
elif sys.argv[1] == '2':
    func = russian_get_text
elif sys.argv[1] == '3':
    func = json_get_text

func(*sys.argv[2:])
