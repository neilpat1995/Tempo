from tempo import app, auth, db
from tempo.models import User

from flask import abort, g, jsonify, make_response, request
from functools import wraps
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
@auth.login_required
def get_recommendations(user_id):
    if g.user.user_id is not user_id:
        return make_response(jsonify({
            'success': False,
            'message': 'user_id does not match'
        }), 400)

    return "Hit /users/user_id/recommendations route!"


'''
Endpoint to upvote/downvote a specific song
'''
@app.route('/users/<int:user_id>/<int:song_id>/<int:is_upvote>', methods=['PUT'])
@auth.login_required
def update_song(user_id, song_id, is_upvote):
    return "Hit /users/user_id/song_id/is_upvote route!"


'''
Handler for nonexistent resources (e.g. invalid user or song)
'''
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
