from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Customer(db.Model):
	c_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(24), nullable=False)
	pw_hash = db.Column(db.String(100), nullable=False)

	#messages = db.relationship('Message', backref='author')

	#follows = db.relationship('User', secondary='follows', primaryjoin='User.user_id==follows.c.follower_id', secondaryjoin='User.user_id==follows.c.followee_id', backref=db.backref('followed_by', lazy='dynamic'), lazy='dynamic')
	
	def __init__(self, username, pw_hash):
		self.username = username
		self.pw_hash = pw_hash

	def __repr__(self):
		return '<Customer {}>'.format(self.username)

class Event(db.Model):
	e_id = db.Column(db.Integer, primary_key=True)
	cid = db.Column(db.Integer, db.ForeignKey('customer.c_id'), nullable=False)
	e_date = db.Column(db.String(50), nullable=False)
	sid_one = db.Column(db.Integer, db.ForeignKey('staff.s_id'), nullable=True)
	sid_two = db.Column(db.Integer, db.ForeignKey('staff.s_id'), nullable=True)
	sid_three = db.Column(db.Integer, db.ForeignKey('staff.s_id'), nullable=True)
	#messages = db.relationship('Message', backref='author')

	#follows = db.relationship('User', secondary='follows', primaryjoin='User.user_id==follows.c.follower_id', secondaryjoin='User.user_id==follows.c.followee_id', backref=db.backref('followed_by', lazy='dynamic'), lazy='dynamic')
	
	def __init__(self,cid, e_date, sid_one, sid_two, sid_three):
		self.cid = cid
		self.e_date = e_date
		self.sid_one = sid_one
		self.sid_two = sid_two
		self.sid_three = sid_three




class Staff(db.Model):
	s_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(24), nullable=False)
	pw_hash = db.Column(db.String(100), nullable=False)

	#messages = db.relationship('Message', backref='author')

	#follows = db.relationship('User', secondary='follows', primaryjoin='User.user_id==follows.c.follower_id', secondaryjoin='User.user_id==follows.c.followee_id', backref=db.backref('followed_by', lazy='dynamic'), lazy='dynamic')
	
	def __init__(self, username, pw_hash):
		self.username = username
		self.pw_hash = pw_hash

	def __repr__(self):
		return '<Staff {}>'.format(self.s_id)


