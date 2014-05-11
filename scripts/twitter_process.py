import twitter
import codecs
import time
from scripts import read_data, write_data

tw = twitter.Api()
tw.SetCredentials('qqq', '111', 'zzz', 'xxx')

def read_twits(inp, output):
    # read tweet ids from <inp>, write tweets (json format)
    # to folder <output>.
    text = read_data(inp)
    was = False
    for line in text:
        idshka, lang = line.split(';')
        while True:
            try:
                limits = tw.GetRateLimitStatus('statuses')[u'resources'][u'statuses'][u'/statuses/show/:id']
                if limits[u'remaining'] <= 10:
                    time.sleep(10)
                else:
                    break
            except:
                time.sleep(10)
        try:
            f = open(output + lang + idshka, 'r')
            f.close()
        except IOError:
            try:
                s = get_one(int(idshka))
                write_data(output + lang + idshka, s.AsJsonString())
            except:
                print 'Twit ' + idshka + ' is hidden now'

def get_one(idshka):
    # request TwitterAPI for tweet with id = <idshka>
    return tw.GetStatus(idshka)  
