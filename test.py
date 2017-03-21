from audio import Audio
from conv_net import ConvNeuralNet, rectify, leaky_rectify, softmax
from net_trainer import NeuralNetTrainer
from utils import load_songs

import csv
import lasagne as L
import numpy as np
import os
import random
import theano
import theano.tensor as T
import time

BASE_SONG_PATH = os.path.dirname(os.path.abspath(__file__)) + '/songs/'

weathers = {
	'sunny': 0,
	'snowy': 1,
	'rainy': 2,
	'cold': 3
}

moods = {
	'excited': 0,
	'sad': 1
}

activities = {
	'chores/work': 0,
	'daily': 1,
	'gym/motivational': 2,
	'meditation': 3,
	'party': 4,
	'relaxation': 5,
	'walking/running': 6,
	'study': 7
}
	
def build_net():
    net = ConvNeuralNet()
    net = net.with_conv_layer(filter_size = (4, 128), num_filters = 256).with_max_pooling_layer(pool_size = (4, 1))
    net = net.with_conv_layer(filter_size = (4, 1), num_filters = 256).with_max_pooling_layer(pool_size = (4, 1))
    net = net.with_dense_layer(0.5, 256)
    net = net.with_output_layer(0.5, 8)

    return net

if __name__ == '__main__':
    data = load_songs('song_labels.csv')
    #random.shuffle(data)

    training_songs = data[0:int(len(data) * 0.75)]
    test_songs = data[int(len(data) * 0.75):]

    # Normalize the values to [0.0, 1.0], but need to
    # find the max value first
    m = 0
    for s in training_songs:
        for i in range(len(s.features.melspectrogram)):
            for j in range(len(s.features.melspectrogram[0])):
                m = max(m, s.features.melspectrogram[i][j])

    #train = training_songs[0:int(len(training_songs) * 0.75)]
    #val = training_songs[int(len(training_songs) * 0.75):]
    train = data
    val = data
    test_songs = data

    x_train = np.array([[s.features.melspectrogram / np.float64(m)] for s in train])
    #y_train = np.array([weathers[s.weather] for s in train])
    #y_train = np.array([moods[s.mood] for s in train])
    y_train = np.array([activities[s.activity] for s in train])

    x_val = np.array([[s.features.melspectrogram / np.float64(m)] for s in val])
	#y_val = np.array([weathers[s.weather] for s in val])
    #y_val = np.array([moods[s.mood] for s in val])
    y_val = np.array([activities[s.activity] for s in val])

    x_test = np.array([[s.features.melspectrogram / np.float64(m)] for s in test_songs])
    #y_test = np.array([weathers[s.weather] for s in test_songs])
    #y_test = np.array([moods[s.mood] for s in test_songs])
    y_test = np.array([activities[s.activity] for s in test_songs])

    net = build_net()

    trainer = NeuralNetTrainer(net)
    trainer.train(
        x_train,
        y_train,
        val_inputs = x_val,
        val_targets = y_val,
        test_inputs = x_test,
        test_targets = y_test,
        learning_rate = 0.01,
        momentum = 0.5,
        batch_size = 2,
        iterations = 100
    )
