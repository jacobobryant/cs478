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


#------------------------------ Intro ------------------------------#

#--------------- 1 ---------------#
dfall_names = pd.read_csv('background/all_names.csv')
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
def main(links_from_ga, all_topics):

	#This will increment every time we find a talk that has no text. Duh.
	speeches_with_no_text, speeches_with_text = 0, 0

	global baby_names
	global all_speeches
	global total_speeches
	global story_names

	print len(links_from_ga)
	short_time = time.time()

	#----- If the output file is empty, initialize it with the column names -----#
	long_factor_list = ['Speech','Gender','WordCount','StoryNames','Popularity','Subjectivity','OT','NT','BoM','PoGP','AllScriptureCount','FleschReading','Talking Speed','AuthorityMentions',
					'WeToYouRatio', 'WordQuantity', 'FirstPersonPronoun', 'PercentInItalics', 'PercentInQuotes', 'Pageviews']
	for i in all_topics:
		try: #It's a str
			long_factor_list.append(i)
		except: #It's a tuple
			long_factor_list.append(i[0])
	#----------------------------------------------------------------------------#


	#3
	for index, value in enumerate(links_from_ga):
		#Read in the stuff correctly
		link, organic_pageviews = value

		#------------------- Verbose -------------------#
		try:
			print "{0}\t{1}".format(index, link)
		except: #sometimes there are strange unicode characters in the URL...
			pass
		
		try:
			#-------------------- a --------------------#
			one_speech = {}
			one_speech['Speech'] = link
			#-------------------- a --------------------#



			#-------------------- b --------------------#
			#b.1
			gender = functions.get_speaker_gender(link, baby_names)
			one_speech['Gender'] = gender

			#b.2
			long_text = functions.get_text_of_page(link)
			speech = functions.just_speech(long_text)

			#b.3
			word_count = functions.get_word_count(speech)
			if word_count < 100: #Then it's for sure not a full speech.
				print 'SKIPPING {0} because: too few words.'.format(link)
				speeches_with_no_text +=1
				continue
			else:
				speeches_with_text +=1
			one_speech['WordCount'] = word_count

			#b.4
			name_mentions = functions.get_name_mentions(speech, story_names)
			one_speech['StoryNames'] = name_mentions

			#b.5
			polarity = functions.get_polarity(speech)
			one_speech['Polarity'] = polarity

			#b.6
			subjectivity = functions.get_subjectivity(speech)
			one_speech['Subjectivity'] = subjectivity

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

			#b.8
			flesch_reading = functions.get_flesch_reading_ease(speech)
			one_speech['FleschReading'] = flesch_reading

			#b.9
			seconds_audio = functions.get_time_elapsed(long_text)
			one_speech['Talking Speed'] = word_count / seconds_audio

			#b.10
			authority_count = functions.get_appeal_to_authority(speech)
			one_speech['AuthorityMentions'] = authority_count

			#b.11
			we_you_ratio = functions.get_we_to_you_ratio(speech)
			one_speech['WeToYouRatio'] = we_you_ratio

			#b.12
			num_different_words = functions.get_how_many_different_words_do_you_use(speech)
			one_speech['WordQuantity'] = num_different_words

			#b.13
			use_of_I = functions.get_use_of_I(speech)
			one_speech['FirstPersonPronoun'] = use_of_I

			#b.14
			words_in_italics = functions.get_words_in_italics(long_text)
			one_speech['PercentInItalics'] = words_in_italics / word_count

			words_in_quotes = functions.get_quotes_in_quotation_marks(speech)
			one_speech['PercentInQuotes'] = words_in_quotes / word_count

			#b.15-b.n
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
					print 'Problem:', link
					continue

			#b.n+1
			organic_pageviews = int(organic_pageviews.replace(',',''))
			one_speech['Pageviews'] = organic_pageviews

			#Add the dictionary to the dictinary of dictionaries.
			all_speeches[link] = one_speech

			#-------------------- b --------------------#
		

		except KeyboardInterrupt: #If you hit Ctrl+C, we'll just skip to the last step with what we have. 


			spit_out_CSV('PARTIAL')
			return


		except Exception as e: #If there's any problem, just don't worry about it.
			print 'SKIPPING ' + link + ' because: ' + str(e)
			pass


	print "\n\nTexted speeches:\t{0}\nUntexted speeches\t{1}".format(speeches_with_text, speeches_with_no_text)
	spit_out_CSV('FULL')
	return
#--------------------------------- Main ----------------------------#

#----------------------- When we're finished -----------------------#
#It'd be great to update this so that it writes out a line every iteration. That way we don't lose our progress if we have to stop...
#It would also have to keep track of where it is.

def spit_out_CSV(how_long):
	global all_speeches
	global start

	#4
	dfout = pd.DataFrame(all_speeches)
	dfout = dfout.transpose()

	#5
	#Time
	print; print
	time_elapsed = time.time()-start
	hours = int(time_elapsed // 3600)
	minutes = int((time_elapsed%3600) // 60)
	seconds = int((time_elapsed%60))

	print "Total time elapsed: {0}hr {1}min {2}sec.".format(hours, minutes, seconds)
	#Out
	dfout.to_csv(how_long+'_speech_popularity.csv', index=False)

	return
#----------------------- When we're finished -----------------------#


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
	end_date = '2017-08-30'
	# end_date = str(datetime.datetime.now()).split(' ')[0]

	start_date = '2016-04-01' #This is when our data got fixes

	d = hello_analytics_api_v3.hello_analytics_main(argv='e', start_date=start_date, end_date=end_date, max_results=10000, metrics='ga:sessions', dimensions='ga:pagePath', samplingLevel='HIGHER_PRECISION', include_empty_rows=False) #10,000 is the highest max_results you can put.

	#This is kind of ugly, but we want to get rid of the nontalks before we start. It will pay off that way.
	#We can't slice it because we need to access the actual values, so we have to use list comprehension. Unfortunate, but it'll still be faster this way.
	d = [i for i in d if i[0][:7]=='/talks/']
	d = [i for i in d if i[0][-4:] not in ['?M=A', '?M=V']]
	d = [i for i in d if i[0][-1]=='/']
	d = [i for i in d if len(i[0])>len('/talks/2016/11/')]


	if len(sys.argv) > 1:
		if sys.argv[1] == 'none':
				print main(d, [])
		else:
			print main(d, sys.argv[1:])
	else:
		print main(d, all_topics)


		