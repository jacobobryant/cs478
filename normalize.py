import pandas as pd 
import sys

#Read in.
df = pd.read_csv('FULL_speech_popularity.csv')

#Set up
unnormalizable = ['Talking Speed', 'Subjectivity', 'Speech', 'PercentInQuotes', 'PercentInItalics', 'WordCount', 'Gender']
to_normalize = [i for i in df.columns if i not in unnormalizable]
normalizer = 'WordCount'

#Normalizer
for i in to_normalize:
	try:
		df[i] = df[i]/df[normalizer]
		mi, ma = df[i].min(), df[i].max()
		df[i] = (df[i] - mi) / (ma-mi)
	except TypeError:
		print i 
		sys.exit(0)

