import json
import time
import os
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack
from werkzeug.security import check_password_hash, generate_password_hash

from models import db, User, Message, Room


app = Flask(__name__)

# configuration
PER_PAGE = 30
DEBUG = True
SECRET_KEY = 'development key'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'chat.db')

app.config.from_object(__name__)
app.config.from_envvar('CHAT_SETTINGS', silent=True)   #(mej) The silent switch just tells Flask to not complain if no such environment key is set.

db.init_app(app)

#items = [[1, 2, 3], ["a", "b", "c"]] #initialize 


welcomePage = """<!DOCTYPE html>
<html>
	<head>
		<title>Welcome to catering company</title>
	</head>
	<p>Welcome to Pitt Catering Company web system!</p>
	<body>
		<form action="" method="post">
			<p>Please login or register:</p>
			<strong><a href="/login">Login Here</a></strong><br>
			<strong><a href="/register">Register Here</a></strong>
		</form>
	</body>
</html>
"""


@app.cli.command('initdb')
def initdb_command():
	#Creates the database tables.
    db.drop_all()
    db.create_all()
    print('Initialized the database.')

@app.before_request
def before_request():
	g.user = None
	if 'user_id' in session:
		g.user = User.query.filter_by(user_id=session['user_id']).first()


def format_datetime(timestamp):
	"""Format a timestamp for display."""
	return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')


@app.route('/', methods=['GET', 'POST'])
def welcome():
	if g.user:
		return redirect(url_for('user_page',username=g.user.username))
	return welcomePage
	#return render_template("theTable.html", items=items)

@app.route('/register', methods=['GET', 'POST'])
def register():
	error = None
	if request.method == 'POST':
		same_un = User.query.filter_by(username=request.form['username']).first()
		if same_un == None:
			db.session.add(User(request.form['username'], request.form['password'],0))     #no encryption
			db.session.commit()
			flash('You were successfully registered and can login now') #display informative message     It creates a message in one view and renders it to a template view function called next.
			return redirect(url_for('login'))
		else:
			error = 'Username already exists. Choose another username'
	return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None

	# if g.user
	if g.user:
		if g.user.room_id>0:
			return redirect(url_for('chatroom', username=g.user.username))
		else:
			return redirect(url_for('user_page',username=g.user.username))

	if request.method=='POST':
		# authentication check
		user =  User.query.filter_by(username=request.form['username']).first()
		if user is None:
			error = 'Invalid Username'
		elif user.pw_hash != request.form['password']:
			error = 'Incorrect password'
		else:
			flash('Successful Login')
			session['user_id'] = user.user_id
			session['recent_id'] = 0
			if user.room_id>0:
				return redirect(url_for('chatroom', username=user.username))
			else:
				return redirect(url_for('user_page',username=user.username))
	return render_template('login.html', error=error)

@app.route('/<username>', methods=['GET', 'POST'])
def user_page(username):
	error =None
	available_rooms=Room.query.all()
	my_rooms=Room.query.filter_by(creator_id=session['user_id']).all()
	return render_template('userPage.html',available_rooms=available_rooms,my_rooms=my_rooms,error=error)

@app.route('/create_room', methods=['POST'])
def create_room():
	db.session.add(Room(session['user_id']))
	db.session.commit()
	my_room = Room.query.filter_by(creator_id=session['user_id']).order_by(Room.room_id.desc()).first()
	r_info = str(my_room.room_id)
	return json.dumps([r_info,])

@app.route('/join_room/<rid>',methods=['POST'])
def join_room(rid):
	error = None
	user = User.query.filter_by(user_id=session['user_id']).first()
	user.room_id=rid
	db.session.commit()
	session['recent_id']=0
	return redirect(url_for('chatroom',username=g.user.username))


@app.route('/chatroom/<username>', methods=['GET', 'POST'])
def chatroom(username):
	error=None
	if not g.user:
		return redirect(url_for('welcome'))

	if g.user.room_id==0:
		return redirect(url_for('user_page',username=g.user.username))

	r_id = g.user.room_id
	messages = Message.query.filter_by(room_id=r_id).order_by(Message.pub_date.asc()).all()
	print('user room id:')
	print(r_id)
	if len(messages)>0:
		session['recent_id']=messages[-1].message_id
		print(session['recent_id'])
	return render_template('chatroom.html',messages=messages,error=error)


@app.route('/add_message', methods=['POST'])
def add_message():
	if 'user_id' not in session:
		abort(401)
	if request.form["msg"]:
		print(request.form["msg"])
		db.session.add(Message(session['user_id'],g.user.room_id, request.form["msg"], int(time.time())))
		db.session.commit()
		flash('Your message was recorded')
	
	#if 'recent_id' not in session:
	#	session['recent_id']=0

	#print('hello hi hi')
	#print(session['recent_id'])
	#new_messages = Message.query.filter(Message.message_id>session['recent_id']).filter(Message.room_id==g.user.room_id).order_by(Message.pub_date.asc()).all()
	text_list = []
	#for m in new_messages:
	#	my_str = get_name(m.author_id)+': '+m.text
	#	text_list.append(my_str)

	#if len(new_messages)>0:
	#s	session['recent_id']=new_messages[-1].message_id

	return json.dumps(text_list)#dump some array as json obj


# backend controller to work with polling
@app.route("/check_message")
def check_message():
	if not g.user:
		return redirect(url_for('welcome'))

	if g.user.room_id==0:
		return redirect(url_for('user_page',username=g.user.username))
	else:
		new_messages = Message.query.filter(Message.message_id>session['recent_id']).filter(Message.room_id==g.user.room_id).order_by(Message.pub_date.asc()).all()
		text_list = []
		for m in new_messages:
			my_str = get_name(m.author_id)+': '+m.text
			text_list.append(my_str)

		if len(new_messages)>0:
			session['recent_id']=new_messages[-1].message_id
		return json.dumps(text_list)


@app.route('/leave_room',methods=['GET', 'POST'])
def leave_room():
	session['recent_id']=0
	user = User.query.filter_by(user_id=session['user_id']).first()
	user.room_id=0
	db.session.commit()
	return redirect(url_for('user_page',username=g.user.username))

@app.route('/delete_room/<rid>',methods=['POST'])
def delete_room(rid):
	error = None
	room_to_delete = Room.query.filter_by(room_id=rid).first()
	if room_to_delete is None:
		abort(404)
	Room.query.filter_by(room_id=rid).delete()
	db.session.commit()
	#delete messages in this room
	Message.query.filter_by(room_id=rid).delete()
	db.session.commit()
	#modify the database
	user_list = User.query.filter_by(room_id=rid).all()
	for user in user_list:
		user.room_id=0
		db.session.commit()
	#inform the users who are currently in this room

	return redirect(url_for('user_page', username=g.user.username))


@app.route("/new_item", methods=["POST"])
def add():
	items.append([request.form["one"], request.form["two"], request.form["three"]])
	#return json.dumps(items)
	return json.dumps([request.form["one"], request.form["two"], request.form["three"]])



@app.route('/logout',methods=['GET', 'POST'])
def logout():
	"""Logs the user out."""
	flash('You were logged out')
	session.clear()
	return redirect(url_for('welcome'))



def get_name(uid):
	stf = User.query.filter_by(user_id=uid).first()
	if stf == None:
		return ''
	else:
		return stf.username + ' '

app.jinja_env.filters['getname'] = get_name

# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime