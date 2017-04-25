from tempo import app, auth, bucket, db, r, s3
from tempo.net import build_user_net, NeuralNetTrainer
from tempo.models import Song, User

from flask import abort, g, jsonify, make_response, request
from functools import wraps
import lasagne
import numpy as np
import pickle
import random
import theano
import theano.tensor as T
from werkzeug import generate_password_hash

'''
Decorator to ensure that the JSON request body
contains the expected keys
'''
def validate_json(*expected_keys):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            json = request.json

            if json is None:
                abort(400)

            for key in expected_keys:
                if key not in json:
                    abort(400)

            return func(*args, **kwargs)

        return wrapper

    return decorator

def validate_query_string(*expected_keys):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            q = request.args

            if q is None:
                abort(400)

            for key in expected_keys:
                if q.get(key) is None:
                    abort(400)

            return func(*args, **kwargs)

        return wrapper

    return decorator

'''
Endpoint to add new user.
Expects a JSON-formatted request with the following structure:
{
	'username': <String>
	'password': <String>
}
'''
@app.route('/users', methods=['POST'])
@validate_json('username', 'password')
def create_user():
    # Salt user password before storing
    _hashed_password = generate_password_hash(request.json['password'])	
    
    new_user = User(request.json['username'], _hashed_password)
    net = build_user_net()
    r.set(username, pickle.dumps(net.params))

    db.session.add(new_user)
    db.session.commit()
    return make_response(jsonify({
        'success': True,
        'user': new_user.as_dict()
    }), 201)

# Route to handle user sign-in; verifies credentials and, if successful, returns an auth token
@app.route('/users/auth', methods=['POST'])
@auth.login_required
def auth_user():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })


'''
Endpoint to get music recommendations for the user
'''
@app.route('/users/<int:user_id>/recommendations', methods=['GET'])
@validate_query_string('weather', 'activity', 'mood')
#@auth.login_required
def get_recommendations(user_id):
    weather = request.args.get('weather')
    activity = request.args.get('activity')
    mood = request.args.get('mood')

    songs = Song.query.filter(Song.weather_type == weather).filter(Song.activity_type == activity).filter(Song.mood_type == mood)

    ret = []
    for song in songs:
        keys = list(bucket.objects.filter(Prefix = song.name).limit(1))

        if len(keys) == 0:
            continue

        key = keys[0]
        ret.append({
            'name': song.name,
            'song_id': song.song_id,
            'url': s3.generate_presigned_url(
                'get_object',
                Params = { 'Bucket': 'tempo-songs', 'Key': key.key },
                ExpiresIn = app.config['AWS_S3_URL_EXPIRATION']
            )
        })

    return jsonify({ 'songs': ret })


'''
Endpoint to upvote/downvote a specific song
'''
@app.route('/users/<int:user_id>/vote', methods = ['PUT'])
@validate_json('song_id', 'is_upvote')
#@auth.login_required
def update_song(user_id):
    song_id = [335, 338, 343, 344, 359]
    is_upvote = request.json['is_upvote']

    #user = User.query.get(user_id)
    #if user is None:
    #    return make_response(jsonify({ 'error': 'invalid user id' }), 400)

    net = build_user_net()
    #net.params = pickle.loads(r.get(user.username))

    m = r.get('mel-max')

    x_train = []
    y_train = []
    for i in song_id:
        song = Song.query.get(i)
        if song is None:
            return make_response(jsonify({ 'error': 'invalid song id' }), 400)

        melspec = list(pickle.loads(r.get(song.name)))
        x_train.append([melspec / np.float64(m)])

        z = random.randint(0, 1)
        print(z)
        y_train.append(z)

    x_train = np.array(x_train)
    y_train = np.array(y_train)

    trainer = NeuralNetTrainer(net)
    trainer.train(
        x_train,
        y_train,
        val_inputs = None,
        val_targets = None,
        test_inputs = None,
        test_targets = None,
        batch_size = 1,
        iterations = 20,
        method = 'adadelta'
    )

    test_prediction = lasagne.layers.get_output(net.net, deterministic = True)
    predict_func = theano.function([net.inputs], [test_prediction])

    ret = {}
    songs = Song.query.all()
    for s in songs:
        if r.get(s.name) is None:
            continue

        melspec = np.array([[list(pickle.loads(r.get(s.name))) / np.float64(m)]])
        conf = predict_func(melspec)

        ret[s.name] = conf

    z = {}
    for k, v in ret.items():
        z[k] = v[0][0][1]

    for k in sorted(z, key = z.get, reverse = True):
        print('{} - {}'.format(k, z[k]))

    print('=' * 20)

    x_train = []
    y_train = []
    for i in [request.json['song_id']]:
        song = Song.query.get(i)
        if song is None:
            return make_response(jsonify({ 'error': 'invalid song id' }), 400)

        melspec = list(pickle.loads(r.get(song.name)))
        x_train.append([melspec / np.float64(m)])

        y_train.append(1)

    x_train = np.array(x_train)
    y_train = np.array(y_train)

    trainer = NeuralNetTrainer(net)
    trainer.train(
        x_train,
        y_train,
        val_inputs = None,
        val_targets = None,
        test_inputs = None,
        test_targets = None,
        batch_size = 1,
        iterations = 10,
        method = 'adadelta'
    )

    test_prediction = lasagne.layers.get_output(net.net, deterministic = True)
    predict_func = theano.function([net.inputs], [test_prediction])

    ret = {}
    songs = Song.query.all()
    for s in songs:
        if r.get(s.name) is None:
            continue

        melspec = np.array([[list(pickle.loads(r.get(s.name))) / np.float64(m)]])
        conf = predict_func(melspec)

        ret[s.name] = conf

    z = {}
    for k, v in ret.items():
        z[k] = v[0][0][1]

    for k in sorted(z, key = z.get, reverse = True):
        print('{} - {}'.format(k, z[k]))



    return jsonify({ 'success': True })


'''
Handler for nonexistent resources (e.g. invalid user or song)
'''
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
