from tempo import app, auth, db

from flask import g
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from werkzeug import check_password_hash

class User(db.Model):
    __tablename__ = 'Users'

    AUTH_TOKEN_EXPIRATION = 7 * 24 * 60 * 60

    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32), index = True, unique = True)
    password = db.Column(db.String(250))

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User: %r>' % self.username

    def as_dict(self):
        dict_object = {
            'user_id': self.user_id,
            'username': self.username
        }
        return dict_object

    def generate_auth_token(self):
        s = Serializer(app.config['SECRET_KEY'], expires_in = User.AUTH_TOKEN_EXPIRATION)
        return s.dumps({ 'user_id': self.user_id }) # encrypt a dictionary and encode user_id within it 

    # Helper function to check if user token is valid and unexpired, used for authenticating user.
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
    # Begin by attempting token authorization
    print(username_or_token)
    user = User.verify_auth_token(username_or_token)
    if not user:
        # Attempt authentication with username and password
        user = User.query.filter_by(username = username_or_token).first()

        if not user or not check_password_hash(user.password, password):
            return False

    g.user = user
    return True
