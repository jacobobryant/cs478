import numpy as np
from scipy import stats
from sklearn.model_selection import train_test_split
import tensorflow as tf
import sys
from argparse import ArgumentParser
from code import interact
from functools import partial

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

    return np.concatenate((gender_features, normalized_data,
                           used_data[:,-1].reshape((-1,1))), axis=1)

def train(model, argv):
    with open('FULL_speech_popularity.csv', 'r') as f:
        contents = f.read()
    train_data, test_data = train_test_split(parse(contents), test_size=0.2)
    valid_attrs = [attr.replace(' ', '') for attr in attributes]
    feature_columns = [tf.feature_column.numeric_column(attr, shape=[1])
                       for attr in valid_attrs[:-1]]

    if model == 'dnn':
        print('using DNNRegressor')
        estimator = tf.estimator.DNNRegressor(hidden_units=[50, 50],
                feature_columns=feature_columns)
    else:
        print('using LinearRegressor')
        estimator = tf.estimator.LinearRegressor(
                feature_columns=feature_columns)

    def input_fn(dataset, num_epochs=None, shuffle=True):
        input_dict = {attr: dataset[:,i]
                      for i, attr in enumerate(valid_attrs[:-1])}
        return tf.estimator.inputs.numpy_input_fn(
                input_dict, dataset[:,-1], batch_size=len(dataset),
                num_epochs=num_epochs, shuffle=shuffle)

    estimator.train(input_fn=input_fn(train_data), steps=1000)
    train_metrics = estimator.evaluate(
            input_fn=input_fn(train_data, 1000, False))
    test_metrics = estimator.evaluate(
            input_fn=input_fn(test_data, 1000, False))

    rmse = lambda metric: metric['average_loss'] ** 0.5
    print("train rmse: %r"% rmse(train_metrics))
    print("test rmse: %r"% rmse(test_metrics))

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('model', nargs='?', default='dnn')
    args = parser.parse_args()

    tf.logging.set_verbosity(tf.logging.INFO)
    tf.app.run(main=partial(train, args.model))
