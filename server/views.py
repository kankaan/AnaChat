from flask import Flask,request, g,Response, render_template, flash, url_for,redirect, stream_with_context, jsonify
from flask_login import LoginManager,login_user, logout_user, current_user, login_required
from urlparse import urlparse, urljoin
from forms import *
from server import app, db, socketio
import itertools
from server import login_manager
from models import *
import time
import functools
from flask_socketio import emit,send, disconnect,join_room, leave_room

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=(user_id)).first()

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if form.validate_on_submit():
        print form.errors
        # Login and validate the user.
        # user should be an instance of your `User` class
        user = User.query.filter_by(username=form.username.data).first()
        if (user == None):
            return render_template('login.html',form=form)
        if (not user.verify_password(form.password.data)):
            return render_template('login.html',form=form)
        login_user(user)

        flash('Logged in successfully.')

        next = request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        if not is_safe_url(next):
            return flask.abort(400)

        return redirect(next or url_for('baseview'))
    return render_template('login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('index.html')

@app.route('/')
@login_required
def index():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data,form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/baseview', methods=['GET','POST'])
@login_required
def baseview():
	print("baseview")
	print(current_user.username)
	chatList = [{'chatName':'first chat','id':2},{'chatName':"second chat with A","id":1}]
	return render_template('userfrontpage.html', username=current_user.username,chatList=chatList, participatedChat=chatList,loggedIn=True)

@app.route('/chat',methods = ['POST'])
@login_required
def chat():
	print("chat")
	messages = ["foo","bar"]
	print("chatID ", request.form['chatID'])
	chatID =  int(request.form['chatID'])
	chat = Chat.query.filter_by(id=chatID).first()
	print(chat.chatname)
	print(chat.messages)
	chatList = [{'chatName':'first chat','id':2},{'chatName':"second chat with A","id":1}]
	for i in chat.messages:
		print(i)
	return render_template('chat.html',
		rows=messages,participatedChat=chatList,currentChatID=chatID)

@app.route('/newChat',methods=['POST'])
@login_required
def newChat():
	print("newChat")
	print(request.form['chatName'])
	print(request.form['chatTitle'])
	chat = Chat(request.form['chatName'],request.form['chatTitle'])
	db.session.add(chat)
	db.session.commit()
	return "newchat created"

@app.route('/chatList', methods=['POST'])
@login_required
def chatList():
	print("chatList")
	print(type(db.session.query(Chat).all()))
	returnQueryList = []
	for i in db.session.query(Chat).all():
		print (i.chatname)
		returnQueryList.append({"chatname":i.chatname,"id":i.id})
	return jsonify(jsonList=returnQueryList)

@app.route('/chatMessage', methods=['POST'])
@login_required
def addChatMessage():
	print(request.form['message'])
	print(current_user.username)
	message = Message(request.form['message'],1)
	print(message)
	db.session.add(message)
	db.session.commit()
	return "ok"


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        print(current_user)
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)

@socketio.on('JSONMessage')
def messageJSON(JSONMessage):
	m = Message(JSONMessage['message'],JSONMessage['room'],current_user.id)
	print(current_user.username, " ja id: ",current_user.id)
	message = current_user.username + ": " + JSONMessage['message'] 
	db.session.add(m)
	db.session.commit()
	socketio.emit("receivedMessage",message,
		room=JSONMessage['room'] )

@socketio.on('connect')
def on_connect():
    send('connected')

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    send(' has entered the room.', room=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    send( ' has left the room.', room=room)

