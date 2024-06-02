from . import db
from datetime import datetime

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    caption = db.Column(db.String(250), nullable=False)
    file = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(600), nullable=True)
    #Adding keywords Task 9 Alex
    keywords = db.Column(db.String(200), nullable=True)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id': self.id,
           'name': self.name,
           'caption': self.caption,
           'file': self.file,
           'desc': self.description,
           'keywords': self.keywords
       }

#Task 9 Alex - Comment to be stored in db
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now, nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'photo_id': self.photo_id,
            'user_id': self.user_id,
            'comment_text': self.comment_text,
            'timestamp': self.timestamp,
        }
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='non-logged-in')

    def __repr__(self):
        return f"User('{self.username}', '{self.role}')"
