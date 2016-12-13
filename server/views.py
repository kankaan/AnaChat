from flask import Flask,request, g,Response, render_template, flash, url_for,redirect, stream_with_context, jsonify
from flask_login import LoginManager,login_user, logout_user, current_user, login_required
from urlparse import urlparse, urljoin
from forms import *
from server import app, db, socketio
import itertools
from server import login_manager
from models import *
import datetime
import functools
from flask_socketio import emit,send, disconnect,join_room, leave_room

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


# page_not_found:
# when user tries to enter to url which isn't valid, Flask redirects to
# baseview
@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('baseview'))

# This funtion is used by flask_login
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=(user_id)).first()

# Login page of the service.
# 
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
            return render_template('login.html',form=form),400
        if (not user.verify_password(form.password.data)):
            return render_template('login.html',form=form),400
        login_user(user)

        flash('Logged in successfully.')

        next = request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        if not is_safe_url(next):
            return flask.abort(400)

        return redirect(next or url_for('baseview'))
    return render_template('login.html', form=form)

#logout function
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('index.html')

# TODO: create landing page for user
@app.route('/')
@login_required
def index():
    return redirect(url_for('login'))


# This function redirects unauthorized users to register page
@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('register'))


# New user registration function.
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if (request.method == 'POST' and form.validate()):
        # check if username already exists in the database
        if (User.query.filter_by(username=form.username.data).first() == None):
            user = User(form.username.data,form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Thanks for registering')
            return redirect(url_for('login'))
        # If nickname is already taken function ends here.
        # This should return something clever, like nick already taken.
        return render_template('register.html',form=form),400
    return render_template('register.html', form=form),400

# chatLists(userID):
# funtion returns either all the chats of the database or
# if the userID is set, the chats of user.
def chatLists(userID = None):
	chatList = []
	if (userID != None):
		chatList = db.session.query(Chat).join(User,Chat.users).filter(User.id == current_user.id).all()
	else:
		chatList = Chat.query.all()
	returnList = []
	for i in chatList:
		chat = {}
		chat['name'] = i.chatname
		chat['title'] = i.topic
		chat['id'] = i.id
		returnList.append(chat)
	return returnList
	
# Baseview is shown for users as a frontpage
# It renders view from template userfrontpage.html and template needs certain values:
# username = name of current user
# chatList = list of chats where user has join
@app.route('/baseview', methods=['GET','POST'])
@login_required
def baseview():
	allChats = chatLists()
	chatList = chatLists(current_user.id)
	return render_template('userfrontpage.html', username=current_user.username,chatList=chatList, participatedChat=chatList,loggedIn=True, allChats=allChats)

# printMessage
# Function takes a message object as a parameter.
# Then function parses chat message from it in an example form:
# (12:12) UserX: "HI!"
def printMessage(sqlObject):
	messageTime = "(" + str(sqlObject.time.hour) + ":" + str(sqlObject.time.minute) + ")"
	senderObj = User.query.filter_by(id=sqlObject.user_id).first()
	senderName = senderObj.username
	return messageTime + " " + senderName + ": " + sqlObject.message 


# Chat page:
# returns a chat page with:
# participatedChat = list of chats where user has join
# rows = list of chat messages
# currentChatID = ID of current chat
@app.route('/chat',methods = ['POST'])
@login_required
def chat():
	if (request.form['chatID'] == None):
		return redirect(url_for('baseview'))
	timeNow = datetime.datetime.now()
	messages = []
	chatID =  int(request.form['chatID'])
	chat = Chat.query.filter_by(id=chatID).first()
    # Only 20 latest messages are shown
	messages = Message.query.filter_by(chat=chatID).order_by(Message.time).limit(20)
	prettify = []
	for i in messages:
		prettify.append(printMessage(i))
	chatList = chatLists(current_user.id)
	return render_template('chat.html', loggedIn=True,
		rows=prettify,participatedChat=chatList,currentChatID=chatID)

# newChat creates a new chat:
# function checks first, if user has provided a name for the chat.
# TODO: Prevent user to creating chats with the same name
@app.route('/newChat',methods=['POST'])
@login_required
def newChat():
	if (request.form['chatName'] != None and request.form['chatTitle'] != None):
		chat = Chat(request.form['chatName'],request.form['chatTitle'])
		db.session.add(chat)
		db.session.commit()
		return "newchat created"
	elif (request.form['chatName'] != None):
		chat = Chat(request.form['chatName'], "")
		db.session.add(chat)
		db.session.commit()
		return "newChat created"
	else:
		return "Provide name for the chat"

# chatList returns a list of all the chats in a JSON format.
@app.route('/chatList', methods=['POST'])
@login_required
def chatList():
	returnQueryList = []
	for i in db.session.query(Chat).all():
		print (i.chatname)
		returnQueryList.append({"chatname":i.chatname,"id":i.id})
	return jsonify(jsonList=returnQueryList)

#this function was propably for the old version
# TODO: check if this is still valid
@app.route('/chatMessage', methods=['POST'])
@login_required
def addChatMessage():
	message = Message(request.form['message'],1)
	db.session.add(message)
	db.session.commit()
	return "ok"

# joinChat:
# this function adds chat for the user and user for the chat in sql point of
# view.
@app.route("/joinChat", methods=['POST'])
@login_required
def joinChat():
	if (request.form['chatID'] == None):
		return redirect(url_for('baseview'))
	user = User.query.filter_by(id=current_user.id).first()
	chatID =  int(request.form['chatID'])
	chat = Chat.query.filter_by(id=chatID).first()
	user.chats.append(chat)
	return redirect(url_for('baseview'))

# autenticated_only is for socket authentication.
# Check: https://flask-socketio.readthedocs.io/en/latest/
def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


@socketio.on('message')
@authenticated_only
def handle_message(message):
    print('received message: ' + message)

# messageJSON is used for broadcasting user messages to other chat members
# The method first creates message instance and saves it to database. Then
# method send it to the audience of the chat.
@socketio.on('JSONMessage')
@authenticated_only
def messageJSON(JSONMessage):
	now = datetime.datetime.now()
	timeNow = "(" + str(now.hour) + ":" + str(now.minute) + ") "
	m = Message(JSONMessage['message'],JSONMessage['room'],
		current_user.id, now)
	message = timeNow + current_user.username + ": " + JSONMessage['message'] 
	db.session.add(m)
	db.session.commit()
	socketio.emit("receivedMessage",message,
		room=JSONMessage['room'] )


# Functions below are not propably needed.
@socketio.on('connect')
@authenticated_only
def on_connect():
    send('connected')

@socketio.on('join')
@authenticated_only
def on_join(data):
    room = data['room']
    join_room(room)
    send(' has entered the room.', room=room)

@socketio.on('leave')
@authenticated_only
def on_leave(data):
    room = data['room']
    leave_room(room)
    send( ' has left the room.', room=room)

