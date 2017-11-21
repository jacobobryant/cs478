import sys
import requests
from html.parser import HTMLParser
import unicodedata
import re
from textblob import TextBlob
from my_textstat import textstatistics as textstat
from os.path import join
from functools import partial
from code import interact
from joblib import Memory
from lxml import etree
from dateutil.parser import parse as parse_date
from datetime import datetime
from urllib.parse import urlencode
import traceback
import secrets

search_engine_id = "017178850987838406603:vp0vn2nince"

memory = Memory(cachedir='joblib_cache', verbose=0)

#dfall_names = pd.read_csv('background/all_names.csv')
#baby_names = dfall_names.values
baby_names = []


OT_books = ['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy', 'Joshua', 'Judges', 'Ruth', 'Samuel', 'Kings', 'Chronicles',
            'Ezra', 'Nehemiah', 'Esther', 'Job', 'Psalm', 'Psalms', 'Proverbs', 'Ecclesiastes', 'Solomon', 'Isaiah', 'Jeremiah', 'Lamentations',
            'Ezekiel', 'Daniel', 'Hosea', 'Joel', 'Amos', 'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai', 
            'Zechariah', 'Malachi']
NT_books = ['Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans', 'Corinthians', 'Galatians', 'Ephesians', 'Philippians', 'Colossians',
            'Thessalonians', 'Timothy', 'Titus', 'Philemon', 'Hebrews', 'James', 'Peter', 'Jude', 'Revelation', 'Revelations']
BoM_books = ['Nephi', 'Jacob', 'Enos', 'Jarom', 'Omni', 'Mormon', 'Mosiah', 'Alma', 'Helaman', 'Ether', 'Moroni']
DyC_books = ['C', 'Covenants'] #Really it's D&amp;amp;C, but \w can't pick up on all that. We're alright.
PoGP_books = ['Moses', 'Abraham', 'History', 'H', 'JSH', 'Faith'] #We're going to lose Joseph Smith - Matthew, but I guess that's ok because really it's a NT book.

def get_story_names():
    #Here we're going to get a list of names that could be in a story. We're going to quantify stories in the speech. So there.
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    other_nonstory_names = ['Jesus', 'Christ', 'Heavenly', 'Young', 'Brigham', 'Son', 'Trinity', 'President', 'Elder', 
                            'Master', 'Smith', 'Heaven', 'Israel', 'America', 'King', 'Dean', 'Will', 'Faith', 'Art']
    names_to_ignore = months + other_nonstory_names


    #Here we're going to get a list of names that could be in a story. We're going to quantify stories in the speech. So there.
    just_names_list = [i[0] for i in baby_names if i[1]+i[2] > 4000] #Only look at reasonably popular names, because sometimes obscure ones are just regular words.
    other_story_names = ['Grandpa', 'Grandma', 'Mom', 'Dad', 'Brother', 'Sister']
    good_story_names = just_names_list + other_story_names

    return set([i for i in good_story_names if i not in names_to_ignore])
story_names = get_story_names()

#def feat_speaker_gender(link):
#    _, speakerlink = link.split('/talks/')
#
#    #Get the speaker's first name.
#    try:
#        speaker, title = speakerlink.split('_')
#    except:
#        speaker = speakerlink
#
#    try:
#        first, last = speaker.split('-') #No middle initial
#    except:
#        if '-and-' in speaker: #It's a combo talk, we're done.
#            gender = 'Combo'
#            return gender
#        else:
#            first, middle, last = speaker.split('-')[:3] #Just the first 3 names
#
#    if len(first) == 1: #If they go by their middle name
#        first = middle
#
#    first = first.title()
#
#    #Ok so now we have the first name, we need to see if it's a male name or a female name
#    try:
#        just_names = list(baby_names[:,0])
#        just_names = list(baby_names[:,0])
#        this_name = baby_names[just_names.index(first)]
#        name, females, males, mfratio = this_name
#
#    except ValueError: #If just_names.index can't find the name we're looking for
#        #---------- Check a lot of unisex names whose gender we know. ------------------#
#        if speaker in set(['terryl-l-givens', 'kerry-m-muhlestein', 'c-terry-warner', 'marion-g-romney', 'val-d-hawks', 'merrill-j-bateman',
#                    'merrill-j-christensen', 'parris-k-egbert', 'angel-abrea', 'marion-d-hanks', 'casey-c-peterson', 'noel-b-reynolds',
#                    'loren-c-dunn', 'terry-r-seamons', 'lee-wakefield', 'val-jo-anderson', 'terry-b-ball', 'lee-h-radebaugh', 'r-quinn-gardner',
#                    'holland-jeffrey-r', 'lee-f-braithwaite', 'mickey-edwards', 'f-enzio-busche', 'uchtdorf-dieter-f', 'alwi-shihab',
#                    'mitt-romney', 'christoffel-golden-jr', 'worthen-kevin-j', 'mcconkie-bruce-r', 'eyring-henry-b', 'callister-tad-r',
#                    'wirthlin-joseph-b', 'callister-douglas-l', 'largey-dennis-l', 'christensen-joe-j', 'oaks-dallin-h', 'groberg-john-h',
#                    'rasband-ronald-a', 'neiger-brad', 'nibley-hugh', 'hinckley-gordon-b', 'rasband-james-r', 'renlund-dale-g', 'osguthorpe-russell-t',
#                    'christensen-clayton', 'hafen-bruce-c', 'swofford-scott', 'packer-boyd-k', 'causse-gerald', 'pinnock-hugh-w', 'featherstone-vaughn-j',
#                    'monson-thomas-s', 'skinner-andrew-c', 'stayner-richards', 'samuelson-cecil-o', 'petersen-mark-e', 'ludlow-victor-l', 'durrant-george',
#                    'hales-robert-d', 'asay-carlos-e', 'cook-gene-r', 'busche-f-enzio', 'kearon-patrick', 'groberg-john-h', 'dunn-michael-l', 'condie-spencer-j',
#                    'wilks-t-jeffery', 'scharffs-brett-g', 'cowley-matthew', 'staheli-donald-l', 'sill-sterling-w', 'bateman-merrill-j', 'pinegar-rex-d', 'welch-john-w',
#                    'j-w-marriott-jr', 'black-susan-easton', 'brough-monte-j', 'erlend-d-peterson', 'backman-robert-l', 'tuttle-theodore-a', 'daines-robert-h', 'givens-terryl-l',
#                    'shumway-eric-b', 'tingey-earl-c', 'kopischke-erich-w', 'echohawk-larry', 'hotchkiss-rollin-h', 'r-j-snow', 'petersen-mark-e', 'steuer-robert-r', 'carmack-john-k',
#                    'hallstrom-donald-l', 'visick-h-hal', 'sonne-alma', 'caffaro-e-j', 'rosenberg-john-r', 'nadauld-stephen-d', 'conlee-robert-k', 'mckinlay-douglas-r', 'luthy-melvin-j',
#                    'britsch-todd-a', 'beeman-richard-r', 'brau-james-c', 'sandberg-jonathan-g', 'adney-y-komatsu', 's-olani-durrant', 'vai-sikahema', 'goaslind-jack-h', 'fyans-j-thomas',
#                    'buehner-carl-w', 'albrecht-w-steve', 'shumway-j-matthew', 'child-sheldon-f', 'kikuchi-yoshihiko', 'paramore-james-m', 'sommerfeldt-scott-d', 'stice-james-d',
#                    'schwendiman-fred-a', 'komatsu-adney-y', 'heperi-vernon-l', 'britsch-r-lanier', 'kowallis-bart-j', 'hanks-marion-d']): #Set searching is faster than list searching
#            return 'Male'
#
#        elif speaker in set(['dwan-j-young', 'sorenson-sorenson', 'dew-sheri-l', 'parkin-bonnie-d', 'abegglen-jo-ann-c', 'baroness-emma-nicholson',
#                        'edmunds-mary-ellen', 'fronk-camille', 'esplin-cheryl-a', 'wilkinson-carol', 'kapp-ardeth-g', 'swinton-heidi-s', 'maughan-erin-d', 'oaks-kristen-m',
#                        'lant-cheryl-c', 'pinegar-patricia-p', 'smoot-mary-ellen', 'nyland-nora-kay', 'nielson-jennifer-b', 'ravert-patricia', 'michaelis-elaine', 'durrant-earlene',
#                        'spafford-belle-s', 'winder-barbara-w', 'funk-ruth-h', 'mouritsen-maren-m', 'penfield-janie', 'clegg-gayle', 'rikelle-richards', 'wixom-rosemary-m', 'samuelson-sharon-g',
#                        'thackeray-rosemary']):
#            return 'Female'
#        else:
#            return 'Unknown'
#        #-------------------------------------------------------------------------------#    
#    
#    #Ok so now we know how many males and females have been named that name, we want to classify the speaker.
#    if males == 0:
#        return 'Female'
#    elif females == 0:
#        return 'Male'
#    elif mfratio > 5:
#        return 'Male'
#    elif mfratio < 0.4:
#        return'Female'
#    
#    else: #if 0.4 <= mfratio <= 5, AND it's not in the top (LONG) list of popular unisex names, we're just going to forget it.
#        return 'Unknown'

def feat_polarity(text):
    Text = TextBlob(text)
    return round(Text.sentiment.polarity, 2)

def feat_subjectivity(text):
    Text = TextBlob(text)
    return round(Text.sentiment.subjectivity, 2)

def feat_word_count(text):
    return textstat(text).lexicon_count()

def feat_flesch_reading_ease(text):
    for i in [';',':']: #We're going to help them out. Semicolons and colons become periods so they count as their own sentence.
        text = text.replace(i, '.')
    
    try:
        return textstat(text).flesch_kincaid_grade()
    except Exception as e: #This will happen if the number of words is 0.
        return -10000.

def book_refs(speech):
    return [book for book in re.findall(r"(\w+) \d{1,3}:\d{1,3}", speech)]

def count_books(book_list, speech):
    return len([b for b in book_refs(speech) if b in book_list])
feat_OT = partial(count_books, OT_books)
feat_NT = partial(count_books, NT_books)
feat_BoM = partial(count_books, BoM_books)
feat_DyC = partial(count_books, DyC_books)
feat_PoGP = partial(count_books, PoGP_books)
feat_all_scripture_count = partial(count_books, OT_books + NT_books +
                                   BoM_books + DyC_books + PoGP_books)

def feat_name_mentions(text):
    #Remove anything in parentheses
    text = re.sub(r'[\(\[][^)]*?[\)\]]', '', text) #Remove anything in parentheses or brackets. Remember the ?, which makes it not greedy.
    #Uppercase AND not (1) beginning a sentence, (2) in a scripture reference, (3) preceeded by 'Elder' or 'President'.
    close_to_what_we_want = re.findall(r"(?<![\.\!\?]\s)(?<!\<p\>)(?<!President\s)(?<!Elder\s)(?<!President\s\w\s)(?<!President\s\w\s\w\s)\b[A-Z][a-z]+\b(?! \d{1,3}:\d{1,3})(?! Smith)", text)
    story_name_mentions = set(close_to_what_we_want).intersection(story_names)
    return len(story_name_mentions)

@memory.cache
def feat_time_elapsed(link):
    long_text = read_file(link, 'Speeches', 'html')
    try:
        url = list(set(re.findall(r'https:\/\/.*\.mp3', long_text)))[0]
    except: #There is no audio URL
        return 10000. #Now the words/second is going to be tiny. But better than it being huge soooo......

    r = requests.get(url, stream=True)

    length_audiofile = r.headers['Content-length']
    seconds = int(length_audiofile) / 6000
    return seconds

def feat_appeal_to_authority(text):
    authority_mentions = re.findall(r'\b(President|Elder|Prophet|of the Quorum of the Twelve)\b', text)
    return len(authority_mentions)

#This isn't precisely the ratio, it's actually (we_count**2) / you_count. This will weight it in favor of lots of 'we's, even if there are a lot of 'you's too.
def feat_we_to_you_ratio(text):
    we_count = len(re.findall(r'\bwe\b', text.lower()))
    you_count = len(re.findall(r'\byou\b', text.lower()))

    try:
        score = round(float(we_count**2) / float(you_count), 3)
    except ZeroDivisionError: #If there are no 'you' mentions, we'll just..... multiply 'we' by 2.
        score = float(we_count * 2)

    return score

def feat_word_quantity(text):
    words = re.findall(r'\b\w+\b', text)
    freq_set = set(words)
    return len(freq_set)

def feat_use_of_I(text):
    say_I = re.findall(r'\bI\b', text)
    return len(say_I)

# This is good at getting quotes, but misses things in quotations.
def feat_words_in_italics(long_text):

    #If there's a Notes section, we'll remove it. Italics will be in references, we don't want those.
    try:
        long_text = long_text[:long_text.index('<b>Notes</b>')]
    except:
        pass


    l = re.findall(r'\<p\>\<i\>.{3,}\<\/i\>.{0,15}\<\/p\>', long_text) #So we're looking for anything that's italicized and on its own line. Also we allow for characters between the <i> and <p> due to <sup>11</sup>, eg.

    all_words_in_italics = ' '.join(l) #We're going to combine this into a single string.
    all_words_in_italics = re.sub(r'\<.{1,3}\>',' ', all_words_in_italics) #and take out the italics and bold parts.

    return feat_word_count(all_words_in_italics)

def feat_quotes_in_quotation_marks(text):
    all_quotes = re.findall(r'\".+?\"', text)
    all_words_in_quotes = ' '.join(all_quotes).replace('"','')
    return feat_word_count(all_words_in_quotes)

def feat_days_elapsed(long_text):
    tree = etree.HTML(long_text)
    raw_date = tree.xpath('//meta[@name="date"]')[0].get('content')
    date = parse_date(raw_date)
    return (datetime.now() - date).days

@memory.cache
def get_num_results(name):
    params = {'key': secrets.google_custom_search_api_key,
              'cx': search_engine_id,
              'q': name}
    query = ("https://www.googleapis.com/customsearch/v1?" +
             "alt=json&fields=queries(request(totalResults))&" +
            urlencode(params))
    response = requests.get(query)
    return int(response.json()['queries']['request'][0]['totalResults'])

def feat_name_search_results(long_text):
    return get_num_results(feat_name(long_text))

def feat_name(long_text):
    tree = etree.HTML(long_text)
    return tree.xpath('//meta[@name="author"]')[0].get('content')

def read_file(link, parent, ext):
    path = join(parent, re.sub(r'^/talks/', '', link).rstrip('/').lower() + '.' + ext)
    with open(path, 'r') as f:
        return f.read()
get_long_text = lambda link: read_file(link, 'Speeches', 'html')
get_speech = lambda link: read_file(link, 'JustWordsSpeeches', 'txt')

if __name__ == '__main__':
    from data import links, pageviews
    import multiprocessing
    import os
    import inspect

    titleize = lambda fn_name: re.sub(r'^feat_', '', fn_name).title().replace('_', '')
    titles, fns = zip(*[(titleize(member), globals()[member])
                        for member in globals() if member.startswith('feat_')])

    def get_features(link):
        try:
            long_text = get_long_text(link)
            speech = get_speech(link)

            def dispatch(f):
                argname = inspect.getargspec(f)[0][0]
                if argname in ('link', 'self'):
                    return f(link)
                elif argname == 'long_text':
                    return f(long_text)
                return f(speech)

            return [dispatch(f) for f in fns]
        except Exception as e:
            if 'No such file or directory' not in str(e):
                traceback.print_exc()
            else:
                print(e, file=sys.stderr)
            return None
    
    pool = multiprocessing.Pool()
    results = [r for r in pool.map(get_features, links)
    #results = [r for r in map(get_features, links)
               if r is not None]
    with open('features.csv', 'w') as outfile:
        print('Pageviews', *titles, sep=',', file=outfile)
        for nviews, features in zip(pageviews, results):
            print(nviews, *features, sep=',', file=outfile)
