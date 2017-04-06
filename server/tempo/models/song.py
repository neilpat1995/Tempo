from tempo import app, db

class Song(db.Model):
    __tablename__ = 'songs'

    song_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255), index = True, unique = True)
    weather_type = db.Column(db.String(32))
    mood_type = db.Column(db.String(32))
    activity_type = db.Column(db.String(32))

    def __init__(self, name, weather_type, activity_type, mood_type):
        self.name = name
        self.weather_type = weather_type
        self.activity_type = activity_type
        self.mood_type = mood_type

    def serialize(self):
        return {
            'name': self.name
        }

    def __repr__(self):
        return '<Song: %r>' % self.name
