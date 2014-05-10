# -*- coding: utf-8 -*-
import os, os.path
import json
import codecs
import nltk
import sys
from scripts import read_data, write_data

def bergsma_get_text(inp, output):
    # extract plain text from tweet in format provided by
    # Shane Bergsma from paper 
    # 'Language Identification for Creating Language-Specific Twitter Collections'.
    data = read_data(inp)

    res = []
    for line in data:
        tokens = line.split('\t')
        if len(tokens) < 3:
            continue
        res.append(tokens[5])
    
    sep = '\n' + '-' * 60 + '\n' * 4
    write_data(output, res, sep)


def plain_get_text(folder, output, prefix=''):
    # writes plain text from every file in <folder> starting with 
    # <prefix> to <output>. 
    files = filter(lambda x: x.startswith(prefix), os.listdir(folder))
    separator = '\n' + '-' * 60 + '\n' * 4
    out_data = []
    for fi in files:
        fi = codecs.open(os.path.join(folder, fi), 'r', 'utf-8')
        out = fi.read()
        out_data.append(out)
        fi.close()

    write_data(output, out_data, separator)

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
        res.append(tokens[3][1:-2])

    sep = '\n' + '-' * 60 + '\n' * 4
    write_data(output, res, sep)

def json_get_text(folder, output, prefix=''):
    # writes json text from every file in <folder> starting with 
    # <prefix> to <output>. 
    files = filter(lambda x: x.startswith(prefix), os.listdir(folder))
    separator = '\n' + '-' * 60 + '\n' * 4
    out_data = []
    for fi in files:
        fi = codecs.open(os.path.join(folder, fi), 'r', 'utf-8')

        out = json.load(fi)[u'text']
        out_data.append(out)
        fi.close()
    
    write_data(output, out_data, separator)

func = bergsma_get_text
if sys.argv[1] == '1':
    func = plain_get_text
elif sys.argv[1] == '2':
    func = russian_get_text
elif sys.argv[1] == '3':
    func = json_get_text

func(*sys.argv[2:])
