#We're going to update this so that it writes out a line every time we go through, so that it doesn't lose its progress.

"""
Arguments to file: (words you want to search the document for)
Note: convert all lists to sets, they are searched quicker.


Method:
1 - Get the database of babynames and google_visits. Also sort out the babynames for the name_mentions function, and names of scripture books.
2 - Initialize an empty dictionary which will eventually contain all the dictionaries, with the key being the speech, and the subdictionary being all the factors.
3 - Run through the speeches:
	a. Initialize a dictionary which will hold the factor for each speech
	b. Get each of the factors: (1) gender. Append.
								(2) get the text of the speech. 
								(3) get just the speech.
								(4) get the word count. If it's less than 100, it probably just says 'The text for this speech is unavailable', so we'll jump to the next link. Otherwise, append.
								(5) get the number of story names.
								(6) polarity. Append.
								(7) subjectivity. Append.
								(8) get the number of scripture references. This is split up into OT, NT, BoM, D&C, PoGP. Append.
								(9) Flesch reading ease. Append.
								(10) Words spoken per second. Append.
								(11) The number of mentions of 'Elder', 'President', or 'Prophet' (capital P). Appeals to authority. Append.
								(12) We/You Ratio. Append.
								(13) The number of different words used (variety). Append.
								(14) Uses of the word "I." This is related to subjectivity, but not super strongly correlated.... hmm...
								(15) get percentage of total words that are in italics (long quotes). Append.
								(16) get percentage of total words that are in quotation marks (short quotes). Append.
								(17-n) The frequency of any words you want. Append each.
								(n+1) The pageviews from that link. Append.
								(n+2) Add the single speech dictionary to the overall dictionary.
4 - Convert the dictionary to a pd.DataFrame. Transpose it so that we have lots of rows, not lots of columns.
5 - Spit out the pd.DataFrame to a CSV: '(FULL|PARTIAL)_speech_popularity.csv'
"""
from __future__ import division

import sys
sys.path.insert(0, '/Users/benjafek/Desktop/GA API/')

import functions
import hello_analytics_api_v3
import pandas as pd
import time
import datetime
import os
import numpy as np 
from tqdm import tqdm


#------------------------------ Intro ------------------------------#

#--------------- 1 ---------------#
dfall_names = pd.read_csv('all_names.csv')
baby_names = dfall_names.values
success = 'Sessions'

#Here we're going to get a list of names that could be in a story. We're going to quantify stories in the speech. So there.
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
other_nonstory_names = ['Jesus', 'Christ', 'Heavenly', 'Young', 'Brigham', 'Son', 'Trinity', 'President', 'Elder', 
						'Master', 'Smith', 'Heaven', 'Israel', 'America', 'King', 'Dean', 'Will', 'Faith', 'Art']
names_to_ignore = months + other_nonstory_names


#Here we're going to get a list of names that could be in a story. We're going to quantify stories in the speech. So there.
just_names_list = [i[0] for i in baby_names if i[1]+i[2] > 4000] #Only look at reasonably popular names, because sometimes obscure ones are just regular words.
other_story_names = ['Grandpa', 'Grandma', 'Mom', 'Dad', 'Brother', 'Sister']
good_story_names = just_names_list + other_story_names

story_names = set([i for i in good_story_names if i not in names_to_ignore])

#Here are lists of each book in each scripture.
OT_books = set(['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy', 'Joshua', 'Judges', 'Ruth', 'Samuel', 'Kings', 'Chronicles',
			'Ezra', 'Nehemiah', 'Esther', 'Job', 'Psalm', 'Psalms', 'Proverbs', 'Ecclesiastes', 'Solomon', 'Isaiah', 'Jeremiah', 'Lamentations',
			'Ezekiel', 'Daniel', 'Hosea', 'Joel', 'Amos', 'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai', 
			'Zechariah', 'Malachi'])
NT_books = set(['Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans', 'Corinthians', 'Galatians', 'Ephesians', 'Philippians', 'Colossians',
			'Thessalonians', 'Timothy', 'Titus', 'Philemon', 'Hebrews', 'James', 'Peter', 'Jude', 'Revelation', 'Revelations'])
BoM_books = set(['Nephi', 'Jacob', 'Enos', 'Jarom', 'Omni', 'Mormon', 'Mosiah', 'Alma', 'Helaman', 'Ether', 'Moroni'])
DyC = set(['C', 'Covenants']) #Really it's D&amp;amp;C, but \w can't pick up on all that. We're alright.
PoGP_books = set(['Moses', 'Abraham', 'History', 'H', 'JSH', 'Faith']) #We're going to lose Joseph Smith - Matthew, but I guess that's ok because really it's a NT book.
#--------------- 1 ---------------#

#--------------- 2 ---------------#
all_speeches = {}
start = time.time()
#--------------- 2 ---------------#


#------------------------------ Intro ------------------------------#


#--------------------------------- Main ----------------------------#
def main(links_from_ga, all_topics, baby_names=baby_names, all_speeches=all_speeches, story_names=story_names):

	#This will increment every time we find a talk that has no text. Duh.
	speeches_with_no_text, speeches_with_text = 0, 0

	tot = len(links_from_ga)
	print (tot)

	#----- If the output file is empty, initialize it with the column names -----#
	long_factor_list = ['Speech','Gender','WordCount','StoryNames','Popularity','Subjectivity','OT','NT','BoM','PoGP','AllScriptureCount','FleschReading','Talking Speed','AuthorityMentions',
					'WeToYouRatio', 'WordQuantity', 'FirstPersonPronoun', 'PercentInItalics', 'PercentInQuotes', 'Pageviews']

	extension = [i if isinstance(i,str) else i[0] for i in all_topics]
	long_factor_list.extend(extension)
	#----------------------------------------------------------------------------#

	#3
	for index in tqdm(range(tot)): #This is only better because enumerate confuses tqdm
		value = links_from_ga[index]

		#Read in the stuff correctly
		link, organic_pageviews = value

		#-------------------- a --------------------#
		one_speech = {}
		one_speech['Speech'] = link
		#-------------------- a --------------------#



		#-------------------- b --------------------#
		start = time.time()
		#b.1
		gender = functions.get_speaker_gender(link, baby_names)
		one_speech['Gender'] = gender

		print ('gender', time.time()-start)
		start = time.time()
		#b.2
		try: #TODO 
			long_text = functions.get_text_of_page(link)
		except IOError as e:
			print (e)
			continue

		print ('get_text', time.time()-start)
		start = time.time()

		speech = functions.just_speech(link)
		if len(speech) < 600: #This has empirically been shown to be good.
			print (speech)
			speeches_with_no_text += 1
			continue
		else:
			speeches_with_text +=1

		print ('speech', time.time()-start)
		start = time.time()
		#b.3
		word_count = functions.get_word_count(speech)
		one_speech['WordCount'] = word_count

		print ('word count', time.time()-start)
		start = time.time()
		#b.4
		name_mentions = functions.get_name_mentions(speech, story_names)
		one_speech['StoryNames'] = name_mentions

		print ('storynames', time.time()-start)
		start = time.time()
		#b.5
		polarity = functions.get_polarity(speech)
		one_speech['Polarity'] = polarity

		print ('polarity', time.time()-start)
		start = time.time()
		#b.6
		subjectivity = functions.get_subjectivity(speech)
		one_speech['Subjectivity'] = subjectivity

		print ('subjectivity', time.time()-start)
		start = time.time()
		#b.7
		scripture_references = functions.get_just_scripture_ref_count(speech, OT_books, NT_books, BoM_books, DyC, PoGP_books)
		ot_count, nt_count, bom_count, dyc_count, pogp_count = scripture_references
		total_scriptures = np.sum(scripture_references)
		
		one_speech['OT'] = ot_count
		one_speech['NT'] = nt_count
		one_speech['BoM'] = bom_count
		one_speech['D&C'] = dyc_count
		one_speech['PoGP'] = pogp_count
		one_speech['AllScriptureCount'] = total_scriptures

		print ('scriptures', time.time()-start)

		start = time.time()
		#b.9
		seconds_audio = functions.get_time_elapsed(long_text)
		one_speech['Talking Speed'] = word_count / seconds_audio

		print ('talkspeed', time.time()-start)
		start = time.time()
		#b.10
		authority_count = functions.get_appeal_to_authority(speech)
		one_speech['AuthorityMentions'] = authority_count

		print ('authority', time.time()-start)
		start = time.time()
		#b.11
		we_you_ratio = functions.get_we_to_you_ratio(speech)
		one_speech['WeToYouRatio'] = we_you_ratio

		print ('weyouratio', time.time()-start)
		start = time.time()
		#b.12
		num_different_words = functions.get_how_many_different_words_do_you_use(speech)
		one_speech['WordQuantity'] = num_different_words

		print ('wordquant', time.time()-start)
		start = time.time()
		#b.13
		use_of_I = functions.get_use_of_I(speech)
		one_speech['FirstPersonPronoun'] = use_of_I


		print ('firstperson', time.time()-start)
		start = time.time()
		#b.14
		words_in_italics = functions.get_words_in_italics(long_text)
		one_speech['PercentInItalics'] = words_in_italics / word_count

		print ('italics', time.time()-start)
		start = time.time()

		words_in_quotes = functions.get_quotes_in_quotation_marks(speech)
		one_speech['PercentInQuotes'] = words_in_quotes / word_count

		print ('quotes', time.time()-start)
		start = time.time()

		#b.15
		speaker_position = functions.get_speaker_position(long_text)
		one_speech['SpeakerPosition'] = speaker_position

		print ('position', time.time()-start)
		start = time.time()

		#b.16-b.n
		for search_word in all_topics: #Here is where we use the word frequency
			if isinstance(search_word, str):
				word_frequency = functions.get_specific_word_frequency(speech, search_word)
				one_speech[search_word] = word_frequency
			elif isinstance(search_word, tuple):
				all_counts = 0
				for each_word in search_word:
					all_counts += functions.get_specific_word_frequency(speech, each_word)
				one_speech[search_word[0]] = all_counts #Notice the [0]. The first word in your tuple should be the word you want to categorize it under.
			else: #we've got a problem.
				continue

		print ('wtopic words', (time.time()-start)/float(len(all_topics)))
		start = time.time()

		#b.n+1
		organic_pageviews = int(organic_pageviews.replace(',',''))
		one_speech['Pageviews'] = organic_pageviews

		print ('pageviews', time.time()-start)

		#Add the dictionary to the dictinary of dictionaries.
		start = time.time()
		all_speeches[link] = one_speech #Because it's a dictionary it loses all order...
		print ('dict:', time.time()-start)

		#-------------------- b --------------------#

		start = time.time()
		spit_out_CSV('PARTIAL')
		print ('spit:', time.time()-start)

	print ("\n\nTexted speeches:\t{0}\nUntexted speeches\t{1}".format(speeches_with_text, speeches_with_no_text))
	spit_out_CSV('FULL')
#--------------------------------- Main ----------------------------#

def spit_out_CSV(how_long):
	global all_speeches
	#4
	dfout = pd.DataFrame(all_speeches)
	dfout = dfout.transpose()
	#5
	#Out
	dfout.to_csv(how_long+'_speech_popularity.csv', index=False)

if __name__ == '__main__':
	#Now this list lines up exactly with the topics on speeches.byu.edu. That will allow us to see how well we classify them automatically.
	all_topics = [('Abrahamic'), #Abrahamic Covenant. SYNONYMS.
				('Accountability', 'Accountable'), #Accountability
				('Adoption', 'Adopt'), #Adoption
				'Agency', #Agency
				('America', 'United States', 'USA'), #America
				('Angel', 'Angelic'), #Angels
				('Articles of Faith', 'Article of Faith'), #Articles of Faith
				'Art', #Arts
				('Atonement', 'Atone'), #Atonement
				'Attitude', #Attitude
				('Authority', 'Authorize'),#Authority

				('Balance', 'Balanced', 'Balancing'), #Balance 
				('Baptism', 'Baptize', 'Baptized'),  #Baptism
				('Bible', 'Biblical'), #Bible
				('Blessing', 'Bless', 'Blessed'), #Blessings
				('Body', 'Bodies'), #Body, Mortal
				'Book of Mormon', #Book of Mormon
				'Brigham Young', #Brigham Young
				('Brotherhood', 'Sisterhood'), #Brotherhood and Sisterhood
				'BYU', #BYU
				
				'Character', #Character
				'Charity', #Charity
				('Chastity', 'Chaste'), #Chastity
				('Children', 'Child'), #Children
				('Christianity', 'Christian'), #Christianity
				'Christmas', #Christmas
				'Calling', #Church Callings
				'Doctrine', #Church Doctrine
				'Growth', #Church Growth
				'Membership', #Church Membership
				'Organization', #Church Organization
				'Church', #Church, the
				('Citizenship', 'Citizen'), #Citizenship
				'Comforter', #Comforter
				('Commandments', 'Command', 'Commanded'), #Commandments
				'Commitment', #Commitment
				('Communication', 'Communicate'), #Communication
				'Compassion', #Compassion
				'Conscience', #Conscience
				'Consecration', #Consecration
				'Contention', #Contention
				'Conversion', #Conversion
				'Courage', #Courage
				'Covenant', #Covenants
				'Creation', #Creation
				'Creativity', #Creativity
				
				('Date', 'Dating'), #Dating
				('Decision', 'Decide'), #Decision-making
				('Dedication', 'Dedicate'), #Dedications
				('Disciple', 'Discipleship'), #Discipleship
				('Discourage', 'Discouraged', 'Discouragement'), #Discouragement
				'Divine', #Divine Nature
				'Potential', #Divine Potential
				'Doctrine and Covenants', #Doctrine and Covenants
				
				'Education', #Education
				'Eternal Life', #Eternal Life
				'Eternity', #Eternity
				('Exaltation', 'Exalt', 'Exalted'), #Exaltation
				'Example', #Example
				('Excellent', 'Excellence', 'Excel'), #Excellence
				
				('Failure', 'Fail'), #Failure
				('Faith', 'Faithful'), #Faith
				'Family', #Family
				'Family History', #Family History
				'Fear', #Fear
				'Fellowship', #Fellowshipping
				'Finance', #Finances
				('Foreordination', 'Foreordain', 'Foreordained'), #Foreordination
				('Forgiveness', 'Forgive', 'Forgave', 'Forgiven'), #Forgiveness
				'Freedom', #Freedom
				('Friendship', 'Friendly', 'Friend'), #Friendship

				'Gift', #Gifts of the Spirit
				('Giving', 'Give'), #Giving
				'God', #God
				'Gospel', #Gospel
				'Government', #Government
				'Gratitude', #Gratitude

				('Habit', 'Habitual'), #Habits
				('Happiness', 'Happy', 'Happier'), #Happiness
				('Heal', 'Healing'), #Healing
				'Heavenly Father', #Heavenly Father
				'Heritage', #Heritage
				'History', #History
				'Holy Ghost', #Holy Ghost
				'Home', #Home
				('Honesty', 'Honest'), #Honesty
				('Honor', 'Honor Code'), #Honor
				('Honor', 'Honor Code'), #Honor Code. ugh.
				'Hope', #Hope
				'Humility', #Humility

				'Individual Worth', #Infividual Worth
				'Initiative', #Initiative
				('Inspiration', 'Inspire', 'Inspired'), #Inspiration
				'Integrity', #Integrity

				'Jesus Christ', #Jesus Christ
				'Joseph Smith', #Joseph Smith
				'Joy', #Joy

				('Kind', 'Kindness'), #Kindness
				'Knowledge', #Knowledge

				'Language', #Language
				'Last Day', #Last Days
				'Law', #Laws
				('Leadership', 'Leader'), #Leadership
				('Learning', 'Learn'), #Learning
				('Life', 'Live'), #Life
				'Light', #Light. ugh.
				'Light of Christ', #Light of Christ
				('Listen', 'Listening'), #Listening
				('Lonely', 'Loneliness'), #Loneliness
				('Love', 'Loving'), #Love

				('Marriage', 'Marry'), #Marriage
				'Media', #Media
				('Meekness', 'Meek'), #Meekness
				('Men', 'Man'), #Men
				'Mercy', 'Miracle', #Mercy
				('Missionary', 'Mission', 'Missionaries'), #Missionary Work
				'Mistake', #Mistakes
				('Modesty', 'Modest'), #Modesty
				'Morality', #Morality
				'Mortality', #Mortality
				'Music', #Music

				'Natural Man', #Natural Man

				('Obedience', 'Obey'), #Obedience
				'Opportunity', #Opportunity
				'Ordinance', #Ordinances

				('Parent', 'Parenthood'), #Parenthood
				('Patience', 'Patient'), #Patience
				'Patriarchal Blessing', #Patriarchal Blessings
				('Patriotism', 'Patriot'), #Patriotism
				'Peer Pressure', #Peer Pressure
				('Perfection', 'Perfect'), #Perfection
				'Perspective', #Perspective
				'Pioneer', #Pioneers
				'Plan of Salvation', #Plan of Salvation
				'Politic', #Politics
				'Power', #Power
				'Prayer', #Prayer
				'Premortal', #Premortal Life
				'Preparation', #Preparation
				('Prepare', 'Preparation'), #Preparation
				'Priesthood', #Priesthood
				('Priority', 'Priorities'), #Priorities
				('Progression', 'Progress'), #Progression
				'Prophet', #Prophets

				'Question', #Questions
				
				'Relationship', #Relationships
				'Religion', #Religion
				('Religious Freedom', 'Religious'), #Religious Freedom
				'Remember', #Remember
				('Repent', 'Repentance'), #Repentance
				('Responsibility', 'Responsible'), #Responsibility
				('Restoration', 'Restore', 'Restored'), #Restoration
				('Resurrection', 'Resurrect', 'Resurrected'), #Resurrection
				('Revelation', 'Reveal'), #Revelation
				('Reverence', 'Reverent'), #Reverence
				('Righteous', 'Righteousness'), #Righteousness

				'Sabbath', #Sabbath Day
				'Sacrament', #Sacrament
				'Sacred', #Sacred
				'Sacrifice', #Sacrifice
				('Safety', 'Safe'), #Safety
				'Salvation', #Salvation
				'Satan', #Satan
				'Scripture', #Scriptures
				'Second Coming', #Second Coming
				'Discipline', #Self-Discipline
				'Esteem', #Self-Esteem
				('Improvement', 'Improve'), #Self-Improvement
				'Self-Reliance', #Self-Reliance
				('Selfless', 'Selflessness'), #Selflessness
				('Service', 'Serve'), #Service
				'Socialism', #Socialism
				'Spirit', #Spirit
				'Spiritual Growth', #Spiritual Growth
				'Spirituality', #Spirituality
				'Standard', #Standards
				'Stewardship', #Stewardship
				('Success', 'Successes' 'Successful'), #Success
				('Suffering', 'Suffer'), #Suffering
				
				('Talent', 'Talented'), #Talents
				('Teaching', 'Teach'), #Teaching
				'Technology', #Technology
				'Temple', #Temples
				('Tempt', 'Temptation'), #Temptation
				'Testimony', #Testimony
				'Thought', #Thoughts
				'Time', #Time Management
				('Tithing', 'Tithe', 'Fast Offering'), #Tithing and Fast Offerings
				('Tolerance', 'Tolerate'), #Tolerance
				'Trial', #Trials
				'Trust', #Trust
				'Truth', #Truth

				('Understand', 'Understanding', 'Understood'), #Understanding
				'Unity', #Unity

				'Value', #Values
				'Virtue', #Virtue

				'War', #War
				('Wisdom', 'Wise'), #Wisdom
				('Witness', 'Witnesses'), #Witness
				('Woman', 'Women'), #Women
				'I am a woman', #Women's Conference
				'Work', #Work
				'Worldly', #Worldliness
				'Worship', #Worship
				('Worthy', 'Worthiness'), #Worthiness
				'Zion'] #Zion
	
	#OK so now that this is allowing for saving and coming back, we don't want the end_date to be RIGHT NOW, because that is subject to change. We'll have it be some recent date.
	end_date = '2017-11-18'

	start_date = '2016-04-01' #This is when our data got fixes

	d = hello_analytics_api_v3.hello_analytics_main(argv='e', start_date=start_date, 
					end_date=end_date, max_results=10000, metrics='ga:sessions', 
					dimensions='ga:pagePath', samplingLevel='HIGHER_PRECISION', 
					include_empty_rows=False, filters='ga:pagePath=~^/talks/.+/$') #10,000 is the highest max_results you can put.

	#This is kind of ugly, but we want to get rid of the nontalks before we start. It will pay off that way.
	#We can't slice it because we need to access the actual values, so we have to use list comprehension. Unfortunate, but it'll still be faster this way.
	d = np.array([i for i in d if len(i[0])>len('/talks/2016/11/')]) #Get rid of just date ones. This shouldn't find any false positives.
	d = np.delete(d, (2788), axis=0) #This talk name is /talks/melissa\xadheath_becoming\xadmore\xadteachable/, so we have to take it out...
	d = np.delete(d, (3207), axis=0) #This talk name is /talks/gayestrathearn_reflections-discipleship/, so we have to take it out...
	d = np.array([i for i in d if i[0].lower()==i[0]]) 

	if len(sys.argv) > 1:
		if sys.argv[1] == 'none':
				main(d, [])
		else:
			main(d, sys.argv[1:])
	else:
		main(d, all_topics)


#TODO I've broken this.