#!venv/bin/python
from flask import Flask
from flask import make_response
from flask import request
from flask import abort
from flask import jsonify
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# Database setup
mysql = MySQL()

# Database configuration
app.config['MYSQL_DATABASE_USER'] = os.environ['TEMPO_DATABASE_USER']
app.config['MYSQL_DATABASE_PASSWORD'] = os.environ['TEMPO_DATABASE_PASSWORD']
app.config['MYSQL_DATABASE_DB'] = os.environ['TEMPO_DATABASE_DB']
app.config['MYSQL_DATABASE_HOST'] = os.environ['TEMPO_DATABASE_HOST']

mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

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
	cursor.callproc('create_user',(request.json['username'],_hashed_password))
	
	data = cursor.fetchall()
	if len(data) is 0:
   		conn.commit()
   		return make_response(jsonify({'Message': 'New user successfully created.'}), 200);
	else:
   		return make_response(jsonify({'Message': str(data[0])}), 1000);

'''
Endpoint to get music recommendations for the user
'''
@app.route('/users/<int:user_id>/recommendations', methods=['GET'])
def get_recommendations(user_id):
	return "Hit /users/user_id/recommendations route!"

'''
Endpoint to upvote/downvote a specific song
'''
@app.route('/users/<int:user_id>/<int:song_id>/<int:is_upvote>', methods=['PUT'])
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
