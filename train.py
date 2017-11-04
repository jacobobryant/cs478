# TODO
# replace parse (and split?) with library functions
# move normalizing code from parse to input_fn?
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
