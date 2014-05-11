# -*- encoding: utf-8 -*-
import codecs

def ISO_639_1_map(lang):
    # returns an ISO-639-1 code for <lang>
    f = [
        ('arabic', 'ar'),
        ('bulgarian', 'bg'),
        ('chuvash', 'cv'),
        ('dutch', 'nl'),
        ('english', 'en'),
        ('farsi', 'fa'),
        ('french', 'fr'),
        ('german', 'de'),
        ('hindi', 'hi'),
        ('italian', 'it'),
        ('marathi', 'mr'),
        ('nepali', 'ne'),
        ('russian', 'ru'),
        ('spanish', 'es'),
        ('tatarcha', 'tt'),
        ('turkish', 'tr'),
        ('ukrainian', 'uk'),
        ('urdu', 'ur')
            ]
    try:
        return dict(f)[lang]
    except KeyError:
        return 'unknown'

def read_data(fi, sep='\n'):
    fi = codecs.open(fi, 'r', 'utf-8')
    data = fi.read().split(sep)
    fi.close()
    return data

def write_data(outp, data, sep='\n'):
    outp = codecs.open(outp, 'w', 'utf-8')
    outp.write(sep.join(data))
    outp.close()

def convert_textcat_to_str(predicted):
    # Converts something like
    # ['Dutch']
    # to 'nl'.
    return ISO_639_1_map(predicted[0])

def convert_cld2_to_str(predicted):
    # Converts something like
    # (True, 97, (('HINDI', 'hi', 98, 661.0), ('Unknown', 'un', 0, 0.0), ('Unknown', 'un', 0, 0.0)))
    # to 'hi'.
    return predicted[2][0][1]

def convert_langid_to_str(predicted):
    # Converts something like
    # ('en', 9.061840057373047)
    # to 'en'.
    return predicted[0]

def out_dict(d):
    # output dictionary in a nice way:
    # 'key1: value1
    #  key2: value2 ... '
    ret = '\n'.join(str(x) + ': ' + str(d[x]) for x in sorted(d.keys()))
    return ret

