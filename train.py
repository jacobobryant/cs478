'''
TODO
replace parse (and split?) with library functions
move normalizing code from parse to input_fn?

example features:
female male gender_unknown WordCount StoryNames Subjectivity OT NT BoM PoGP AllScriptureCount FleschReading TalkingSpeed AuthorityMentions WeToYouRatio WordQuantity FirstPersonPronoun PercentInItalics PercentInQuotes Pageviews
100.0 101.0 100.0 103.742120616 99.6661046269 99.6600383632 99.6604019113 99.6618275902 99.6703816637 99.6596890719 99.6753715398 99.6645221234 99.6613725488 99.6653917875 99.8212819345 100.733938127 99.7381014116 99.6597290267 99.6597276576
10.0 11.0 10.0 13.6535132269 9.69606787422 9.66015000762 9.66058200946 9.66058200946 9.65981057761 9.65981057761 9.6613534413 9.66504859982 9.66156528001 9.6613534413 9.6721534871 11.0383592804 9.66983919157 9.65988284813 9.65992814758
8925.0 8926.0 8925.0 8928.71734822 8924.67221336 8924.67013243 8924.66967564 8924.67136745 8924.66967564 8924.66967564 8924.67644291 8924.67640907 8924.67165882 8924.67052155 8924.68832792 8925.83618358 8924.70097425 8924.6697087 8924.66968483
'''
import numpy as np
from scipy import stats
import tensorflow as tf

raw_attributes = ['WordCount', 'StoryNames', 'Subjectivity', 'OT', 'NT', 'BoM',
        'PoGP', 'AllScriptureCount', 'FleschReading', 'Talking Speed',
        'AuthorityMentions', 'WeToYouRatio', 'WordQuantity',
        'FirstPersonPronoun', 'PercentInItalics', 'PercentInQuotes',
        'Pageviews']
attributes = ["female", "male", "gender_unknown"] + raw_attributes

def parse(csv_contents):
    raw_data = [line.split(',') for line in csv_contents.split('\n')]
    headers = raw_data[0]

    indices = [headers.index(attr) for attr in raw_attributes]
    used_data = np.array(raw_data[1:])[:,indices].astype(float)
    normalized_data = stats.zscore(used_data[:,:-1], axis=1)

    def gender_vector(gender):
        if gender == 'female':
            return [1, 0, 0]
        elif gender == 'male':
            return [0, 1, 0]
        return [0, 0, 1]

    gender_index = headers.index('Gender')
    gender_features = np.array([gender_vector(row[gender_index].lower())
                                for row in raw_data[1:]], dtype=float)

    features = np.concatenate((gender_features, normalized_data), axis=1)
    labels = used_data[:,-1]
    return features, labels

def split(features, labels, test_fraction=0.2):
    indices = np.random.permutation(len(features))
    test_index = int(len(features) * test_fraction)
    test_indices, train_indices = indices[:test_index], indices[test_index:]
    return (features[train_indices], labels[train_indices],
            features[test_indices], labels[test_indices])

def main(train_features, train_labels, test_features, test_labels):
    valid_attrs = [attr.replace(' ', '') for attr in attributes]
    #print(*valid_attrs)
    #for i in (0, 1, 2):
    #    print(*(train_features[i] + [train_labels[i]]))
    #return

    feature_columns = [tf.feature_column.numeric_column(attr, shape=[1])
                       for attr in valid_attrs[:-1]]
    estimator = tf.estimator.LinearRegressor(feature_columns=feature_columns)

    input_dict = {attr: train_features[:,i]
                  for i, attr in enumerate(valid_attrs[:-1])}

    input_fn = tf.estimator.inputs.numpy_input_fn(
            input_dict, train_labels, batch_size=len(train_features),
            num_epochs=None, shuffle=True)

    train_input_fn = tf.estimator.inputs.numpy_input_fn(
            input_dict, train_labels, batch_size=len(train_features),
            num_epochs=1000, shuffle=False)

    test_input_dict = {attr: test_features[:,i]
                       for i, attr in enumerate(valid_attrs[:-1])}
    test_input_fn = tf.estimator.inputs.numpy_input_fn(
            test_input_dict, test_labels, batch_size=len(test_features),
            num_epochs=1000, shuffle=False)

    estimator.train(input_fn=input_fn, steps=1000)

    rmse = lambda metric: metric['average_loss'] ** 0.5
    train_metrics = estimator.evaluate(input_fn=train_input_fn)
    test_metrics = estimator.evaluate(input_fn=test_input_fn)
    print("train rmse: %r"% rmse(train_metrics))
    print("test rmse: %r"% rmse(test_metrics))
    # train rmse: 5188.7229642755065
    # test rmse: 3089.2152725247233


if __name__ == "__main__":
    with open('FULL_speech_popularity.csv', 'r') as f:
        contents = f.read()
    main(*split(*parse(contents)))
