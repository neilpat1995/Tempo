from tempo import app, db, r
from tempo.analysis import Audio
from tempo.models import Song
from tempo.net import ConvNeuralNet, NeuralNetTrainer

import boto3
#from boto.s3.connection import S3Connection
import csv
from flask import jsonify, make_response
import numpy as np
import os
import pickle

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

'''
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
'''

activities = {
    'daily': 0,
    'exercise': 1,
    'focused': 2,
    'party': 3
}
	

@app.route('/train', methods = ['POST'])
def train():
    song_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../songs')
    songs = [f for f in os.listdir(song_dir) if os.path.isfile(os.path.join(song_dir, f))]

    '''
    for index, song in enumerate(songs):
        name = song.lstrip().rstrip()
        print('%d - %s' % (index, name))
        clip = Audio(os.path.join(song_dir, song)).slice(45)
        print('%d x %d' % (len(clip.features.pitches), len(clip.features.pitches[0])))
        r.set('%s - pitch' % name, pickle.dumps(clip.features.pitches))
    '''

    '''
    file_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../training_data/song_labels.csv')
    with open(file_name, 'r') as f:
        reader = csv.DictReader(f)
        i = 0

        names = []
        for row in reader:
            song = Song(
                row['Song Name'].lstrip(),
                row['Weather'].lower(),
                row['Activity'].lower(),
                row['Mood'].lower()
            )

            if song.name in names:
                continue

            names.append(song.name)

            db.session.add(song)

        db.session.commit()
    '''

    weather_net = ConvNeuralNet()
    weather_net = weather_net.with_conv_layer(filter_size = (4, 128), num_filters = 256).with_max_pooling_layer(pool_size = (4, 1))
    #weather_net = weather_net.with_conv_layer(filter_size = (4, 969), num_filters = 256).with_max_pooling_layer(pool_size = (4, 1))
    weather_net = weather_net.with_conv_layer(filter_size = (4, 1), num_filters = 256).with_max_pooling_layer(pool_size = (4, 1))
    weather_net = weather_net.with_dense_layer(0.5, 256)
    weather_net = weather_net.with_output_layer(0.5, 4)

    train = csv.DictReader(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../training_data/activity_train.csv'), 'r'))
    test = csv.DictReader(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../training_data/activity_test.csv'), 'r'))

    m = 0
    x_train = []
    y_train = []
    for row in train:
        name = row['name'].lstrip().rstrip()

        try:
            melspec = list(pickle.loads(r.get(name)))
            #melspec = list(pickle.loads(r.get('%s - pitch' % name)))
            for i in range(len(melspec)):
                for j in range(len(melspec[0])):
                    m = max(m, melspec[i][j])

            x_train.append(melspec)
            y_train.append(activities[row['activity_type'].replace(' ', '')])
        except:
            print('not found: %s' % name)

            if os.path.exists(os.path.join(song_dir, name)):
                clip = Audio(os.path.join(song_dir, name)).slice(45)
                melspec = clip.features.melspectrogram
                r.set(name, pickle.dumps(melspec))

                x_train.append(melspec)
                y_train.append(activities[row['activity_type'].replace(' ', '')])

                for i in range(len(melspec)):
                    for j in range(len(melspec[0])):
                        m = max(m, melspec[i][j])

    x_test = []
    y_test = []
    for row in test:
        name = row['name'].lstrip().rstrip()

        try:
            melspec = list(pickle.loads(r.get(name)))
            #melspec = list(pickle.loads(r.get('%s - pitch' % name)))

            for i in range(len(melspec)):
                for j in range(len(melspec[0])):
                    m = max(m, melspec[i][j])

            x_test.append(melspec)
            y_test.append(activities[row['activity_type'].replace(' ', '')])
        except:
            print('not found: %s' % name)

            if os.path.exists(os.path.join(song_dir, name)):
                clip = Audio(os.path.join(song_dir, name)).slice(45)
                melspec = clip.features.melspectrogram
                r.set(name, pickle.dumps(melspec))

                x_test.append(melspec)
                y_test.append(activities[row['activity_type'].replace(' ', '')])

                for i in range(len(melspec)):
                    for j in range(len(melspec[0])):
                        m = max(m, melspec[i][j])

    r.set('mel-max', m)
    x_train = np.array([[mel / np.float64(m)] for mel in x_train])
    y_train = np.array(y_train)

    x_test = np.array([[mel / np.float64(m)] for mel in x_test])
    y_test = np.array(y_test)

    '''
    train_data = []
    for row in train:
        print(row['name'])
        song = list(songs.objects.filter(Prefix = row['name']).limit(1))[0]
        print('downloading %s' % song.key)
        songs.download_file(song.key, song.key)
        a = Audio(song.key)
        print(a.features.melspectrogram)
        os.remove(song.key)

        #for s in songs.list(prefix = row['name']):
        #    print(s.name)
        break
    '''

    trainer = NeuralNetTrainer(weather_net)
    trainer.train(
        x_train,
        y_train,
        val_inputs = None,
        val_targets = None,
        test_inputs = x_test,
        test_targets = y_test,
        learning_rate = 0.01,
        momentum = 0.5,
        batch_size = 10,
        #learning_rate = 0.0001,
        #momentum = 0.9,
        #batch_size = 20,
        iterations = 100,
        method = 'momentum'
    )
    

    '''
    activity_net = ConvNeuralNet()
    activity_net = activity_net.with_conv_layer(filter_size = (4, 128), num_filters = 256).with_max_pooling_layer(pool_size = (4, 1))
    activity_net = activity_net.with_conv_layer(filter_size = (4, 1), num_filters = 256).with_max_pooling_layer(pool_size = (4, 1))
    activity_net = activity_net.with_dense_layer(0.5, 256)
    activity_net = activity_net.with_output_layer(0.5, 8)

    mood_net = ConvNeuralNet()
    mood_net = mood_net.with_conv_layer(filter_size = (4, 128), num_filters = 256).with_max_pooling_layer(pool_size = (4, 1))
    mood_net = mood_net.with_conv_layer(filter_size = (4, 1), num_filters = 256).with_max_pooling_layer(pool_size = (4, 1))
    mood_net = mood_net.with_dense_layer(0.5, 256)
    mood_net = mood_net.with_output_layer(0.5, 8)

    params = pickle.loads(r.get('weather_net'))
    if params is not None:
        weather_net.params = params
    else:
        r.set('weather_net', pickle.dumps(weather_net.params))

    params = pickle.loads(r.get('activity_net'))
    if params is not None:
        activity_net.params = params
    else:
        r.set('activity_net', pickle.dumps(activity_net.params))

    params = pickle.loads(r.get('mood_net'))
    if params is not None:
        mood_net.params = params
    else:
        r.set('mood_net', pickle.dumps(mood_net.params))
    '''

    return make_response(jsonify({
        'success': True
    }), 200)
