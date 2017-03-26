#!venv/bin/python
from flask import Flask
from flask import make_response
from flask import request
from flask import abort
from flask import jsonify
from werkzeug import generate_password_hash, check_password_hash
import os
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from flask_sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth

# Configure app and other utilities
app = Flask(__name__)
auth = HTTPBasicAuth()

db_user = os.environ['TEMPO_DATABASE_USER']
db_password = os.environ['TEMPO_DATABASE_PASSWORD']
db_name = os.environ['TEMPO_DATABASE_DB']
db_host = os.environ['TEMPO_DATABASE_HOST']
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s/%s' %(db_user, db_password, db_host, db_name)
db = SQLAlchemy(app)

# app.config['MYSQL_DATABASE_USER'] = os.environ['TEMPO_DATABASE_USER']
# app.config['MYSQL_DATABASE_PASSWORD'] = os.environ['TEMPO_DATABASE_PASSWORD']
# app.config['MYSQL_DATABASE_DB'] = os.environ['TEMPO_DATABASE_DB']
# app.config['MYSQL_DATABASE_HOST'] = os.environ['TEMPO_DATABASE_HOST']

# mysql.init_app(app)

# conn = mysql.connect()
# cursor = conn.cursor()

class User(db.Model):
	__tablename__ = 'Users'
	user_id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(32), index = True, unique = True)
	password = db.Column(db.String(128))

	def __init__(self, username, password):
		self.username = username
		self.password = password

	def __repr__(self):
		return '<User %r>' % self.username

	def generate_auth_token(self, expiration = 600):
		s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
		return s.dumps({ 'id': self.user_id })

	@staticmethod
	def verify_auth_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except SignatureExpired:
			return None # valid token, but expired
		except BadSignature:
			return None # invalid token
		user = User.query.get(data['user_id'])
		return user

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

'''
Endpoint to add new user.
Expects a JSON-formatted request with the following structure:
{
	'username': <String>
	'password': <String>
}
'''
@app.route('/users', methods=['POST'])
def create_user():
	# Validate request
	if not request.json:
		abort(400)
	if not 'username' in request.json:
		abort(400)
	if type(request.json['username']) is not unicode:
		abort(400)
	if not 'password' in request.json:
		abort(400)
	if type(request.json['password']) is not unicode:
		abort(400)

	_hashed_password = generate_password_hash(request.json['password'])	# Salt user password before storing
	# cursor.callproc('create_user',(request.json['username'],_hashed_password)) # Call stored procedure on database instance to create user
	new_user = User(request.json['username'], _hashed_password)
	db.session.add(new_user)
	db.session.commit()

	if (User.query.filter_by(username=request.json['username']).first() is not None):
		return make_response(jsonify({'new_user': new_user.__dict__}), 200);
	else:
   		return make_response(jsonify({'Error': 'New user could not be created.'}), 1000);


@app.route('/users/auth', methods=['POST'])
@auth.login_required
def auth_user():
	token = g.user.generate_auth_token()
	return jsonify({ 'token': token.decode('ascii') })
	# # Validate request
	# if not request.json:
	# 	abort(400)
	# if not 'username' in request.json or not 'password' in request.json:
	# 	abort(400)
	# if type(request.json['username']) is not unicode or type(request.json['password']) is not unicode:
	# 	abort(400)
	# # Validate user
	# _hashed_password = generate_password_hash(request.json['password'])	# Find hashed password for query
	# validation_query = "SELECT * FROM Users WHERE Username = {0} AND Password = {1}".format(request.json['username'], _hashed_password)
	# cursor.execute()
	# result = cursor.fetchone()
	# if result is None:
	# 	return make_response(jsonify({'error': 'Invalid credentials.'}), 401)
	
	# # Generate auth token


'''
Endpoint to get music recommendations for the user
'''
@app.route('/users/<int:user_id>/recommendations', methods=['GET'])
@auth.login_required
def get_recommendations(user_id):
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

if __name__ == '__main__':
	app.run(debug=True)
