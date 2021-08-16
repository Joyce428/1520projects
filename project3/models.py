from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(24), nullable=False)
	pw_hash = db.Column(db.String(100), nullable=False)
	room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'), nullable=False) #default as 0

	#messages = db.relationship('Message', backref='author')

	#follows = db.relationship('User', secondary='follows', primaryjoin='User.user_id==follows.c.follower_id', secondaryjoin='User.user_id==follows.c.followee_id', backref=db.backref('followed_by', lazy='dynamic'), lazy='dynamic')
	
	def __init__(self, username, pw_hash, room_id):
		self.username = username
		self.pw_hash = pw_hash
		self.room_id = room_id

	def __repr__(self):
		return '<User {}>'.format(self.username)

class Message(db.Model):
	message_id = db.Column(db.Integer, primary_key=True)
	author_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
	room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'), nullable=False)
	text = db.Column(db.Text, nullable=False)
	pub_date = db.Column(db.Integer)

	def __init__(self, author_id, room_id, text, pub_date):
			self.author_id = author_id
			self.room_id = room_id
			self.text = text
			self.pub_date = pub_date

	def __repr__(self):
			return '<Message {}'.format(self.message_id)



class Room(db.Model):
	room_id = db.Column(db.Integer, primary_key=True)
	creator_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

	#pw_hash = db.Column(db.String(100), nullable=False)

	#messages = db.relationship('Message', backref='author')

	#follows = db.relationship('User', secondary='follows', primaryjoin='User.user_id==follows.c.follower_id', secondaryjoin='User.user_id==follows.c.followee_id', backref=db.backref('followed_by', lazy='dynamic'), lazy='dynamic')
	
	def __init__(self, creator_id):
		self.creator_id = creator_id

	def __repr__(self):
		return '<Room {}>'.format(self.room_id)


