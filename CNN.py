import numpy as np
from scipy import stats
from sklearn.model_selection import train_test_split
import tensorflow as tf
import sys
from argparse import ArgumentParser
from code import interact
from functools import partial
from math import sqrt

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

def get_data():
    with open('FULL_speech_popularity.csv', 'r') as f:
        contents = f.read()
    train_data, test_data = train_test_split(parse(contents), test_size=0.2)
    valid_attrs = [attr.replace(' ', '') for attr in attributes]
    feature_columns = [tf.feature_column.numeric_column(attr, shape=[1])
                       for attr in valid_attrs[:-1]]
    return train_data, test_data

train, test = get_data()
tr_pv, tt_pv = train[:, -1], test[:, -1]
tr_d, tt_d = train[:, :-1], test[:, :-1]

input_data = tf.placeholder(tf.float32, [1, 3, 3, 2])
y_true = tf.placeholder(tf.float32, [1, 1])

with tf.variable_scope("CNN") as scope:
    w0 = tf.layers.conv2d(input_data, 1, 1, 1, padding = "SAME", activation = tf.nn.relu, name = "w0", kernel_initializer = tf.contrib.layers.variance_scaling_initializer())
    w1 = tf.layers.conv2d(w0, 128, 5, 2, padding = "SAME", activation = tf.nn.relu, name = "w1", kernel_initializer = tf.contrib.layers.variance_scaling_initializer())
    w2 = tf.layers.conv2d(w1, 256, 5, 2, padding = "SAME", activation = tf.nn.relu, name = "w2", kernel_initializer = tf.contrib.layers.variance_scaling_initializer())
    w3 = tf.layers.conv2d(w2, 512, 5, 2, padding = "SAME", activation = tf.nn.relu, name = "w3", kernel_initializer = tf.contrib.layers.variance_scaling_initializer())
    w3 = tf.reshape(w3, [1, int(np.prod(w3.shape))])
    w4 = tf.layers.dense(w3, 1, name="w4", kernel_initializer = tf.contrib.layers.variance_scaling_initializer())

with tf.name_scope('loss') as scope:
    loss = tf.losses.mean_squared_error(labels = y_true, predictions = w4)

train = tf.train.AdamOptimizer(1e-3).minimize(loss)

init=tf.global_variables_initializer()
saver = tf.train.Saver()
sess=tf.Session()
sess.run(init)

for j in range(100):
    for i, dp in enumerate(tr_d):
        dp = dp[:-1]
        dp_new = np.reshape(dp, (1, 3,3,2))
        t, l = sess.run([train, loss], feed_dict={input_data: dp_new, y_true: [[tr_pv[i]]]})
        print(sqrt(l))
