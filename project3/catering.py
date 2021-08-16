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

glob_username = None


welcomePage = """<!DOCTYPE html>
<html>
	<head>
		<title>Welcome to catering company</title>
	</head>
	<p>Welcome to Pitt Catering Company web system!</p>
	<body>
		<form action="" method="post">
			<p>Please select your system role:</p>
			<input type="radio" id="worker" name="role" value="worker">
			<label for="worker">Company Staff/Owner</label><br>
			<input type="radio" id="customer" name="role" value="customer">
			<label for="customer">Customer</label><br>
			<input type="submit" value="Enter System" />
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


@app.route('/register', methods=['GET', 'POST'])
def register_customer():
	error = None
	if request.method == 'POST':
		#db.session.add(Customer(request.form['username'], generate_password_hash(request.form['password'])))    #with password encryption
		same_un = Customer.query.filter_by(username=request.form['username']).first()
		if same_un == None:
			db.session.add(Customer(request.form['username'], request.form['password']))     #no encryption
			db.session.commit()
			flash('You were successfully registered and can login now') #display informative message     It creates a message in one view and renders it to a template view function called next.
			return redirect(url_for('cus_login'))
		else:
			error = 'Username already exists. Choose another username'
	return render_template('register.html', error=error)

@app.route('/', methods=['GET', 'POST'])
def welcome():
	#check_cus()
	if 'cus_id' in session:
		cus = Customer.query.filter_by(c_id=session['cus_id']).first()
		if cus is not None:
			return redirect(url_for('request_event',username=cus.username))
	#check_worker()
	if 'worker_id' in session:
		if session['worker_id']==0:
			return redirect(url_for('admin'))
		else:
			stf = Staff.query.filter_by(s_id=session['worker_id']).first()
			if stf is not None:
				return redirect(url_for('work_event',username=stf.username))

	if request.method=='POST':
		if request.form.get('role') == 'customer':
			session['role']=1    # role =1  if logging in as customer; role=0 if logging in as staff/owner
			return redirect(url_for('cus_login'))
		elif request.form.get('role') == 'worker':
			session['role']=0    # role =1  if logging in as customer; role=0 if logging in as staff/owner
			return redirect(url_for('company_login'))
	return welcomePage
	#return redirect(url_for('login'))



@app.route('/customer-login', methods=['GET', 'POST'])
def cus_login():
	error = None
	if 'cus_id' in session:
		cus =  Customer.query.filter_by(c_id=session['cus_id']).first()
		return redirect(url_for('request_event',username=cus.username))
	if 'worker_id' in session:
		if session['worker_id']==0:
			print('hello3')
			return redirect(url_for('admin'))
		else:
			stf = Staff.query.filter_by(s_id=session['worker_id']).first()
			if stf is not None:
				return redirect(url_for('work_event',username=stf.username))

	if request.method=='POST':
		# authentication check
		cus =  Customer.query.filter_by(username=request.form['username']).first()
		if cus is None:
			error = 'Invalid Username'
		elif cus.pw_hash != request.form['password']:
			error = 'Incorrect password'
		else:
			flash('Successful Login')
			session['cus_id'] = cus.c_id
			session['username']=cus.username
			return redirect(url_for('request_event', username=cus.username))
	return render_template('login.html', error=error)


@app.route('/company-login', methods=['GET', 'POST'])
def company_login():
	error = None
	if request.method=='POST':
		# authentication check
		if request.form['username']=='owner':
			if request.form['password']=='pass':
				session['worker_id'] = 0 # 0 means administrator
				session['username'] = 'owner'
				return redirect(url_for('admin'))
		else:
			stf =  Staff.query.filter_by(username=request.form['username']).first()
			if stf is None:
				error = 'Invalid Username'
			elif stf.pw_hash != request.form['password']:
				error = 'Incorrect password'
			else:
				flash('Successful Login')
				session['worker_id'] = stf.s_id
				session['username'] = stf.username
				return redirect(url_for('work_event',username=stf.username))
	return render_template('login.html', error=error)



@app.route('/admin',methods=['GET','POST'])
def admin():
	error=None
	#msg=''
	my_events=[]
	my_events = Event.query.order_by(Event.e_date.asc()).all()	

	return render_template('owner_page.html',my_events=my_events, error=error)


@app.route('/create-staff-account',methods=['GET','POST'])
def create_staff():
	error=None
	
	if request.method == 'POST':
		if 'staffun' in request.form:
			same_un = Staff.query.filter_by(username=request.form['staffun']).first()
			if same_un is None:
				db.session.add(Staff(request.form['staffun'], request.form['staffps']))     #no encryption
				db.session.commit()
				flash('You successfully created a new staff') #display informative message     It creates a message in one view and renders it to a template view function called next.
				return redirect(url_for('admin'))
			else:
				error = 'That username already exists'
		else:
			return redirect(url_for('welcome'))
	return render_template('register.html', error=error)


# load staff page
@app.route('/work-event/<username>', methods=['GET', 'POST'])
def work_event(username):
	error=None
	if 'worker_id' in session:
		if session['worker_id']>0:
			error = None
			my_events = Event.query.filter((Event.sid_one==session['worker_id'])|(Event.sid_two==session['worker_id'])|(Event.sid_three==session['worker_id'])).order_by(Event.e_date.asc()).all()
			need_staff = Event.query.filter((Event.sid_one==None)|(Event.sid_two==None)|(Event.sid_three==None)).order_by(Event.e_date.asc()).all()
			#TEST
			 #intersection: evt needing more staff & evt I scheduled
			other_events = list(set(need_staff) - set(list(set(my_events) & set(need_staff)))) # evt needing more staff & evt I DID NOT schedule
			return render_template('staff_page.html', my_events=my_events, other_events=other_events, error=error)
	else:
		return render_template('staff_page.html', error=error)

@app.route('/join-event/<eid>',methods=['POST'])
def join_event(eid):
	error = None
	if 'worker_id' not in session:
		abort(401)
	event_to_join = Event.query.filter_by(e_id=eid).first()
	if event_to_join is None:
		abort(404)	
	if event_to_join.sid_one == None:
		event_to_join.sid_one = session['worker_id']
		db.session.commit()
	elif event_to_join.sid_two == None:
		event_to_join.sid_two = session['worker_id']
		db.session.commit()
	elif event_to_join.sid_three == None:
		event_to_join.sid_three = session['worker_id']
		db.session.commit()

	stf = Staff.query.filter_by(s_id=session['worker_id']).first()
	if stf is not None:
		return redirect(url_for('work_event', username= stf.username))
	else:
		return render_template('staff_page.html', error=error)

@app.route('/customer-cancel-event/<eid>',methods=['POST'])
def customer_cancel(eid):
	error = None
	event_to_cancel = Event.query.filter_by(e_id=eid).first()
	if event_to_cancel is None:
		abort(404)
	Event.query.filter_by(e_id=eid).delete()
	db.session.commit()
	return check_cus()


@app.route('/staff-cancel-event/<eid>',methods=['POST'])
def staff_cancel(eid):
	error = None
	if 'worker_id' not in session:
		abort(401)
	event_to_cancel = Event.query.filter_by(e_id=eid).first()
	if event_to_cancel is None:
		abort(404)
	if event_to_cancel.sid_one == session['worker_id']:
		event_to_cancel.sid_one = None
		db.session.commit()
	elif event_to_cancel.sid_two == session['worker_id']:
		event_to_cancel.sid_two = None
		db.session.commit()
	elif event_to_cancel.sid_three == session['worker_id']:
		event_to_cancel.sid_three = None
		db.session.commit()

	stf = Staff.query.filter_by(s_id=session['worker_id']).first()
	if stf is not None:
		return redirect(url_for('work_event', username= stf.username))
	else:
		return render_template('staff_page.html', error=error)


@app.route('/request-event/<username>', methods=['GET', 'POST'])
def request_event(username):
	error=None
	error_msg=''
	if request.method=='POST':
		if Event.query.filter_by(e_date=request.form['event_date']).first() is None:
			db.session.add(Event(session['cus_id'],request.form['event_date'], None,None,None))    
			db.session.commit()
		else:
			error_msg='The company is already booked for the date you requested. Please select another date:'
	cus_events=Event.query.filter_by(cid=session['cus_id']).order_by(Event.e_date.asc()).all()
	return render_template('customer_page.html', msg = error_msg, cus_events=cus_events,error=error)



#@app.before_request
#def before_request():
def check_cus():
	if 'cus_id' in session:
		cus = Customer.query.filter_by(c_id=session['cus_id']).first()
		if cus is not None:
			#session.pop('cus_id',None)
			#return welcomePage
			print('hello')
			return redirect(url_for('request_event',username=cus.username))
	#else:
	#	return welcomePage

def check_worker():
	if 'worker_id' in session:
		if session['worker_id']==0:
			print('hello3')
			return redirect(url_for('admin'))
		else:
			stf = Staff.query.filter_by(s_id=session['worker_id']).first()
			if stf is not None:
				return redirect(url_for('work_event',username=stf.username))
	#else:
		#return welcomePage


@app.route('/logout',methods=['GET', 'POST'])
def logout():
	"""Logs the user out."""
	flash('You were logged out')
	session.clear()
	return redirect(url_for('welcome'))



def get_name(sid):
	stf = Staff.query.filter_by(s_id=sid).first()
	if stf == None:
		return ''
	else:
		return stf.username + ' '

app.jinja_env.filters['getname'] = get_name