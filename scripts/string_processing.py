# -*- coding: utf-8 -*-
import nltk
import re, string

def cut_punct(text):
    for punct in string.punctuation:
        text = text.replace(punct, '')
        #text = text.replace(punct, ' ') # part of adv processing
    return text

def cut_whitespace(text):
    # any sequence of ' ' -> one ' '
    # any number of '\n' -> one ' '
    # starting with whitespace -> cut
    text = re.sub("\s+", ' ', text)
    if len(text) and text[0] == ' ':
        text = text[1:]
    if len(text) and text[-1] == ' ':
        text = text[:-1]
    return text

def get_links(text):
    # checks only for  'http://...' and 'www...'
    text = text + ' '
    pat = "http://.*?\s"
    links = nltk.regexp_tokenize(text, pat)
    text = ' ' + text + ' '
    pat = '\swww\..*?\..*?\s'
    links.extend(nltk.regexp_tokenize(text, pat))
    links = map(lambda x: x[:-1], links)
    return links

def get_mentions(text):
    # entities starting with '@'
    text = text + ' '
    pat = "@.*?[:\s]"
    mentions = nltk.regexp_tokenize(text, pat)
    mentions = map(lambda x: x[:-1], mentions)
    return mentions

def get_hashtags(text):
    # entities starting with '#'
    text = text + ' '
    pat = "#.*?\s"
    tags = nltk.regexp_tokenize(text, pat)
    tags = map(lambda x: x[:-1], tags)
    return tags

def cut_digits(text):
    # digits are irrelevant for text
    for digit in string.digits:
        text = text.replace(digit, '')
    return text

def cut_repost(text):
    # 'RT' stands for 'retweet', which is irrelevant
    text = text.replace(' RT ', '')
    if text.startswith('RT'):
        text = text[2:]
    text = text.replace('&gt;', '') # weird html stuff appearing
    return text

def shorten_equal(text):
    # reduces occurences of 3 or more consecutive letter to two.
    expr = '%s{3,}'
    for letter in set(text):
        text = re.sub(expr % letter, letter + letter, text)
    return text
        

def cut_short_words(text):
    # delete all words shorter than 3
    words = []
    for word in text.split(' '):
        if len(word) >= 3:
            words.append(word)
    return ' '.join(words)

def process(text):
    text = cut_repost(text)
    links = get_links(text)
    mentions = get_mentions(text)
    hashtags = get_hashtags(text)
    for link in links:
        text = text.replace(link, '')
    for tag in hashtags:
        text = text.replace(tag, '')
    for mention in mentions:
        text = text.replace(mention, '')
    text = cut_punct(text)
    text = cut_digits(text)
    text = cut_whitespace(text)
    #text = shorten_equal(text) # part of adv processing
    #text = cut_short_words(text) # part of adv processing
    #text = text.lower() # part of adv processing
    return text
