"""
This file contains the functions which main.py calls, in this order:
1. get_speaker_gender(link)
2. get_speech_content(link)
3. just_speech(html_text)
4. get_polarity(text)
5. get_subjectivity(text)
6. get_word_count(text)
7. get_reading_level(text)
8. get_ref_count(text)
9. get_just_scripture_count(long_text)
10. get_word_frequency(text, word)
11. get_organic_pageviews(link)
12. get_name_mentions(text, story_names)
13. 
"""
import sys
sys.path.append('/Users/benjafek/Desktop/MakePopularityCSV/background/') #With this, we'll be able to import from background/

import requests
import HTMLParser
import unicodedata
import re
from textblob import TextBlob
from my_textstat import textstatistics #from background.
from bs4 import BeautifulSoup



#1
def get_speaker_gender(link, baby_names):
	#Just the unique part of the URL
	talks = '/talks/'
	speakerlink = link[link.index(talks)+len(talks):]

	#Get the speaker's first name.
	try:
		speaker, title = speakerlink.split('_')
	except:
		speaker = speakerlink

	try:
		first, last = speaker.split('-') #No middle initial
	except:
		if '-and-' in speaker: #It's a combo talk, we're done.
			gender = 'Combo'
			return gender
		else:
			first, middle, last = speaker.split('-')[:3] #Just the first 3 names

	if len(first) == 1: #If they go by their middle name
		first = middle

	first = first.title()

	#Ok so now we have the first name, we need to see if it's a male name or a female name
	try:
		just_names = list(baby_names[:,0])
		this_name = baby_names[just_names.index(first)]
		name, females, males, mfratio = this_name

	except ValueError: #If just_names.index can't find the name we're looking for
		#---------- Check a lot of unisex names whose gender we know. ------------------#
		if speaker in set(['terryl-l-givens', 'kerry-m-muhlestein', 'c-terry-warner', 'marion-g-romney', 'val-d-hawks', 'merrill-j-bateman',
					'merrill-j-christensen', 'parris-k-egbert', 'angel-abrea', 'marion-d-hanks', 'casey-c-peterson', 'noel-b-reynolds',
					'loren-c-dunn', 'terry-r-seamons', 'lee-wakefield', 'val-jo-anderson', 'terry-b-ball', 'lee-h-radebaugh', 'r-quinn-gardner',
					'holland-jeffrey-r', 'lee-f-braithwaite', 'mickey-edwards', 'f-enzio-busche', 'uchtdorf-dieter-f', 'alwi-shihab',
					'mitt-romney', 'christoffel-golden-jr', 'worthen-kevin-j', 'mcconkie-bruce-r', 'eyring-henry-b', 'callister-tad-r',
					'wirthlin-joseph-b', 'callister-douglas-l', 'largey-dennis-l', 'christensen-joe-j', 'oaks-dallin-h', 'groberg-john-h',
					'rasband-ronald-a', 'neiger-brad', 'nibley-hugh', 'hinckley-gordon-b', 'rasband-james-r', 'renlund-dale-g', 'osguthorpe-russell-t',
					'christensen-clayton', 'hafen-bruce-c', 'swofford-scott', 'packer-boyd-k', 'causse-gerald', 'pinnock-hugh-w', 'featherstone-vaughn-j',
					'monson-thomas-s', 'skinner-andrew-c', 'stayner-richards', 'samuelson-cecil-o', 'petersen-mark-e', 'ludlow-victor-l', 'durrant-george',
					'hales-robert-d', 'asay-carlos-e', 'cook-gene-r', 'busche-f-enzio', 'kearon-patrick', 'groberg-john-h', 'dunn-michael-l', 'condie-spencer-j',
					'wilks-t-jeffery', 'scharffs-brett-g', 'cowley-matthew', 'staheli-donald-l', 'sill-sterling-w', 'bateman-merrill-j', 'pinegar-rex-d', 'welch-john-w',
					'j-w-marriott-jr', 'black-susan-easton', 'brough-monte-j', 'erlend-d-peterson', 'backman-robert-l', 'tuttle-theodore-a', 'daines-robert-h', 'givens-terryl-l',
					'shumway-eric-b', 'tingey-earl-c', 'kopischke-erich-w', 'echohawk-larry', 'hotchkiss-rollin-h', 'r-j-snow', 'petersen-mark-e', 'steuer-robert-r', 'carmack-john-k',
					'hallstrom-donald-l', 'visick-h-hal', 'sonne-alma', 'caffaro-e-j', 'rosenberg-john-r', 'nadauld-stephen-d', 'conlee-robert-k', 'mckinlay-douglas-r', 'luthy-melvin-j',
					'britsch-todd-a', 'beeman-richard-r', 'brau-james-c', 'sandberg-jonathan-g', 'adney-y-komatsu', 's-olani-durrant', 'vai-sikahema', 'goaslind-jack-h', 'fyans-j-thomas',
					'buehner-carl-w', 'albrecht-w-steve', 'shumway-j-matthew', 'child-sheldon-f', 'kikuchi-yoshihiko', 'paramore-james-m', 'sommerfeldt-scott-d', 'stice-james-d',
					'schwendiman-fred-a', 'komatsu-adney-y', 'heperi-vernon-l', 'britsch-r-lanier', 'kowallis-bart-j', 'hanks-marion-d']): #Set searching is faster than list searching
			return 'Male'

		elif speaker in set(['dwan-j-young', 'sorenson-sorenson', 'dew-sheri-l', 'parkin-bonnie-d', 'abegglen-jo-ann-c', 'baroness-emma-nicholson',
						'edmunds-mary-ellen', 'fronk-camille', 'esplin-cheryl-a', 'wilkinson-carol', 'kapp-ardeth-g', 'swinton-heidi-s', 'maughan-erin-d', 'oaks-kristen-m',
						'lant-cheryl-c', 'pinegar-patricia-p', 'smoot-mary-ellen', 'nyland-nora-kay', 'nielson-jennifer-b', 'ravert-patricia', 'michaelis-elaine', 'durrant-earlene',
						'spafford-belle-s', 'winder-barbara-w', 'funk-ruth-h', 'mouritsen-maren-m', 'penfield-janie', 'clegg-gayle', 'rikelle-richards', 'wixom-rosemary-m', 'samuelson-sharon-g',
						'thackeray-rosemary']):
			return 'Female'
		else:
			return 'Unknown'
		#-------------------------------------------------------------------------------#	
	
	#Ok so now we know how many males and females have been named that name, we want to classify the speaker.
	if males == 0:
		return 'Female'
	elif females == 0:
		return 'Male'
	elif mfratio > 5:
		return 'Male'
	elif mfratio < 0.4:
		return'Female'
	
	else: #if 0.4 <= mfratio <= 5, AND it's not in the top (LONG) list of popular unisex names, we're just going to forget it.
		return 'Unknown'

#2 #This will get us everything that is encoded into the webpage. Then we'll shimmy it down in just_speech()
# Actually, update this so that we're just reading what we've already downloaded.
def get_text_of_page(link):	
	fname = link.split('/')[2]
	with open('Speeches/{}.html'.format(fname)) as f:
		html = f.read()

	parser = HTMLParser.HTMLParser()
	em_dash = parser.unescape("&#8212;") #This is an em-dash!
	html = html.replace(em_dash, ' - ') #Instead of those, we want space-dash-space.

	#Changing out fancy left and right quotations for regular quotations is important for getting quotes.
	left_quote = parser.unescape("&#8220;") 
	right_quote = parser.unescape("&#8221;") 
	for quotes in [left_quote, right_quote]:
		html = html.replace(quotes, '"')

	
	html = unicodedata.normalize('NFKD', html).encode('ascii', 'ignore')
	return html

#3
def just_speech(html, first_words='<p>', last_words='All rights reserved.'):
	soup = BeautifulSoup(html, 'html.parser')
	l = soup.find_all(name=['p'])
	speech = '\n'.join(list([str(i) for i in l]))
	# speech = soup.meta(['content'])
	return speech

#4
def get_polarity(text):
	Text = TextBlob(text)
	return round(Text.sentiment.polarity, 2)

#5
def get_subjectivity(text):
	Text = TextBlob(text)
	return round(Text.sentiment.subjectivity, 2)

#6
def get_word_count(text):
	TS = textstatistics(text)
	return TS.lexicon_count()

#7
def get_flesch_reading_ease(text):
	for i in [';',':']: #We're going to help them out. Semicolons and colons become periods so they count as their own sentence.
		text = text.replace(i, '.')
	
	TS = textstatistics(text)

	try:
		grade_level = TS.flesch_kincaid_grade()
		return grade_level
	except Exception as e: #This will happen if the number of words is 0.
		return -10000.

#8
def get_just_scripture_ref_count(speech, OT_books, NT_books, BoM_books, DyC, PoGP_books): #These are sets.
	#This will get us any scripture reference.
	scripture_references = set(re.findall(r"\w+ \d{1,3}:\d{1,3}", speech)) #This will look like 'BOOK ###:###'. And we don't want repeats.

	#Now split it up into books
	each_book_count = [0,0,0,0,0] #[ot, nt, bom, dyc, pogp]
	for i in scripture_references:
		book, scripture = i.split(' ')
		if book in OT_books: 
			each_book_count[0] += 1
		elif book in NT_books: 
			each_book_count[1] += 1 
		elif book in BoM_books: 
			each_book_count[2] += 1
		elif book in DyC: 
			each_book_count[3] += 1
		elif book in PoGP_books: 
			each_book_count[4] += 1
		else:
			pass #It's something else (probably a time).

	return each_book_count

#9. TODO Maybe instead of word frequency, we really want if they mentioned it at all. Like more than (4) times or something.
def get_specific_word_frequency(text, word):
	match = re.findall(r"\b%s\b" % word.lower(), text.lower()) #r makes it a raw string. \b looks for breakwords.
	matches = re.findall(r"\b%s\b" % (word.lower()+'s'), text.lower()) #Also if there's just an s at the end, we'll count it.
	return len(match) + len(matches)

#10
def get_organic_pageviews(link, google_data, success='Sessions'):
	if link[:7] != '/talks/': #Then it probably got entered as the full URL. We need it to just begin with /talks/
		try:
			link = link[link.index('/talks/'):]
		except ValueError: #It couldn't find '/talks/'
			raise ValueError("Argument 'link' must be a URL from a talk on speeches.byu.edu")

	#Now, find the success value (probably 'Sessions') of that talk
	all_talks = list(google_data[:,0])
	talk_data = google_data[all_talks.index(link)]

	organic_pageviews = int(talk_data[-1].replace(',',''))
	return organic_pageviews

#11
def get_name_mentions(text, story_names):
	#Remove anything in parentheses
	text = re.sub(r'[\(\[][^)]*?[\)\]]', '', text) #Remove anything in parentheses or brackets. Remember the ?, which makes it not greedy.
	#Uppercase AND not (1) beginning a sentence, (2) in a scripture reference, (3) preceeded by 'Elder' or 'President'.
	close_to_what_we_want = re.findall(r"(?<![\.\!\?]\s)(?<!\<p\>)(?<!President\s)(?<!Elder\s)(?<!President\s\w\s)(?<!President\s\w\s\w\s)\b[A-Z][a-z]+\b(?! \d{1,3}:\d{1,3})(?! Smith)", text)
	story_name_mentions = set(close_to_what_we_want).intersection(story_names)
	return len(story_name_mentions)
	
#12
def get_time_elapsed(long_text):
	try:
		url = list(set(re.findall(r'https:\/\/.*\.mp3', long_text)))[0]
	except: #There is no audio URL
		return 10000. #Now the words/second is going to be tiny. But better than it being huge soooo......

	r = requests.get(url, stream=True)

	try:
		length_audiofile = r.headers['Content-length']
	except KeyError:
		return 10000.

	seconds = int(length_audiofile) / 6000

	return seconds

#13
def get_appeal_to_authority(text):
	authority_mentions = re.findall(r'\b(President|Elder|Prophet|of the Quorum of the Twelve)\b', text)
	return len(authority_mentions)

#14. This isn't precisely the ratio, it's actually (we_count**2) / you_count. This will weight it in favor of lots of 'we's, even if there are a lot of 'you's too.
def get_we_to_you_ratio(text):
	we_count = len(re.findall(r'\bwe\b', text.lower()))
	you_count = len(re.findall(r'\byou\b', text.lower()))

	try:
		score = round(float(we_count**2) / float(you_count), 3)
	except ZeroDivisionError: #If there are no 'you' mentions, we'll just..... multiply 'we' by 2.
		score = float(we_count * 2)

	return score

#15.
def get_how_many_different_words_do_you_use(text):
	words = re.findall(r'\b\w+\b', text)
	freq_set = set(words)
	return len(freq_set)


#16.
def get_use_of_I(text):
	say_I = re.findall(r'\bI\b', text)
	return len(say_I)

#17. This is good at getting quotes, but misses things in quotations.
def get_words_in_italics(long_text):

	#If there's a Notes section, we'll remove it. Italics will be in references, we don't want those.
	try:
		long_text = long_text[:long_text.index('<b>Notes</b>')]
	except:
		pass


	l = re.findall(r'\<p\>\<i\>.{3,}\<\/\i\>.{0,15}\<\/p\>', long_text) #So we're looking for anything that's italicized and on its own line. Also we allow for characters between the <i> and <p> due to <sup>11</sup>, eg.

	all_words_in_italics = ' '.join(l) #We're going to combine this into a single string.
	all_words_in_italics = re.sub(r'\<.{1,3}\>',' ', all_words_in_italics) #and take out the italics and bold parts.

	return get_word_count(all_words_in_italics)

#18.
def get_quotes_in_quotation_marks(text):
	all_quotes = re.findall(r'\".+?\"', text)
	all_words_in_quotes = ' '.join(all_quotes).replace('"','')
	return get_word_count(all_words_in_quotes)

#19. So this will tell us the speaker's position, we just have to figure out what format to put this in. 
#Maybe come up with some scoring scheme?
#Problem: some of the people who should have titles aren't listed.
def get_speaker_position(long_text):
	speaker_position = re.findall(r'(?<=\<span class="speech__speaker-position"\>).+?(?=\<\/span\>)', long_text)
	return speaker_position

