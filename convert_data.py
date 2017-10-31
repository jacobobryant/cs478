import numpy as np
from functools import lru_cache
from scipy import stats

#features = ['Speech', 'Gender', 'WordCount', 'StoryNames', 'Popularity',
#            'Subjectivity', 'OT', 'NT', 'BoM', 'PoGP', 'AllScriptureCount',
#            'FleschReading', 'Talking Speed', 'AuthorityMentions', 'WeToYouRatio',
#            'WordQuantity', 'FirstPersonPronoun', 'PercentInItalics',
#            'PercentInQuotes', 'Pageviews']

features = ['WordCount', 'StoryNames', 'Popularity',
            'Subjectivity', 'OT', 'NT', 'BoM', 'PoGP', 'AllScriptureCount',
            'FleschReading', 'Talking Speed', 'AuthorityMentions', 'WeToYouRatio',
            'WordQuantity', 'FirstPersonPronoun', 'PercentInItalics',
            'PercentInQuotes', 'Pageviews']

with open('FULL_speech_popularity.csv', 'r') as f:
    raw_data = [line.split(',') for line in f.read().split('\n')]

headers = raw_data[0]
gender_index = headers.index('Gender')
#pageviews_index = headers.index('Pageviews')

def gender_vector(row_index):
    gender = raw_data[row_index][gender_index].lower()
    if gender == 'female':
        return [1, 0, 0]
    elif gender == 'male':
        return [0, 1, 0]
    return [0, 0, 1]

existing_features = [f for f in features if f in headers]
indices = [headers.index(feat) for feat in existing_features]
float_data = np.array([[float(x) for x in row]
                       for i, row in enumerate(np.array(raw_data[1:])[:,indices])])
normalized_data = np.array([stats.zscore(col) for col in float_data[:,:-1].transpose()]).transpose()
final_data = np.concatenate((np.array([np.append(gender_vector(i + 1), row)
                                      for i, row in enumerate(normalized_data)]),
                             float_data[:,-1].reshape(1,-1).T), axis=1)

with open('data.arff', 'w') as f:
    print('@relation speeches', file=f)
    for ef in ['Female', 'Male', 'Unknown'] + existing_features:
        print("@attribute '{}' numeric".format(ef), file=f)
    print('@data', file=f)
    for row in final_data:
        print(*row, sep=',', file=f)
