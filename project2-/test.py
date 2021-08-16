import time
import os
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack
from werkzeug.security import check_password_hash, generate_password_hash

from models import db, Customer, Event, Staff

app = Flask(__name__)

# configuration
PER_PAGE = 30
DEBUG = True
SECRET_KEY = 'development key'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'catering.db')

app.config.from_object(__name__)
app.config.from_envvar('CATERING_SETTINGS', silent=True)   #(mej) The silent switch just tells Flask to not complain if no such environment key is set.

db.init_app(app)

@app.cli.command('initdb')
def initdb_command():
	#Creates the database tables.
    db.drop_all()
    db.create_all()
    print('Initialized the database.')

@app.cli.command('testr')
def request_event():
	mystr ="22222222222222222222222222222222222222222222222222"
	#db.session.add(Event(5, mystr,3, None, None))
		#db.session.add(Event(session['user_id'], "2011-03-15",None, None, None))
	#db.session.commit()
	db.session.add(Customer('hello1', 'hello2'))     #no encryption
	db.session.commit()

	print(type(request.form['event_date']))

