from flask import request, render_template, flash, \
                    url_for, redirect, jsonify
from flask_login import login_user, logout_user, current_user, \
                        login_required
from urllib.parse import urlparse, urljoin
from .forms import RegistrationForm, LoginForm
from server import app, db, socketio, login_manager
from .models import User, Message, Chat
from . import logger

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


# page_not_found:
# when user tries to enter to url which isn't valid, Flask redirects to
# baseview
@app.errorhandler(404)
def page_not_found():
    return redirect(url_for('baseview'))

# This funtion is used by flask_login
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=(user_id)).first()

# Login page of the service.
#
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        logger.debug(form.errors)
        # Login and validate the user.
        # user should be an instance of your `User` class
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            return render_template('login.html', form=form), 400
        if not user.verify_password(form.password.data):
            return render_template('login.html', form=form), 400
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
    return redirect(url_for('index'), code=307)

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
    if request.method == 'POST' and form.validate():
        # check if username already exists in the database
        if User.query.filter_by(username=form.username.data).first() is None:
            user = User(form.username.data, form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Thanks for registering')
            return redirect(url_for('login'))
        # If nickname is already taken function ends here.
        # This should return something clever, like nick already taken.
        return render_template('register.html', form=form), 400
    return render_template('register.html', form=form), 400

# chatLists(userID):
# funtion returns either all the chats of the database or
# if the userID is set, the chats of user.
def chatLists(userID=None):
    chats = []
    if userID != None:
        chats = db.session.query(Chat).join(User, Chat.users). \
                        filter(User.id == current_user.id).all()
    else:
        chats = Chat.query.all()
    returnList = []
    for i in chats:
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
@app.route('/baseview', methods=['GET', 'POST'])
@login_required
def baseview():
    allChats = chatLists()
    chatList = chatLists(current_user.id)
    return render_template('userfrontpage.html', username=current_user. \
        username, chatList=chatList, participatedChat=chatList, loggedIn=True, \
        allChats=allChats)

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
@app.route('/chat', methods=['POST'])
@login_required
def chat():
    if request.form['chatID'] is None:
        return redirect(url_for('baseview'))
    messages = []
    chatID = int(request.form['chatID'])
    chat = Chat.query.filter_by(id=chatID).first()
    # Only 20 latest messages are shown
    messages = Message.query.filter_by(chat=chatID).order_by(Message.time).limit(20)
    prettify = []
    for i in messages:
        prettify.append(printMessage(i))
    chatList = chatLists(current_user.id)
    return render_template('chat.html', loggedIn=True, \
        rows=prettify, participatedChat=chatList, currentChatID=chatID)

# newChat creates a new chat:
# function checks first, if user has provided a name for the chat.
@app.route('/newChat', methods=['POST'])
@login_required
def newChat():
    if request.form['chatName'] != None and request.form['chatTitle'] != None:
        chat = Chat(request.form['chatName'], request.form['chatTitle'])
        db.session.add(chat)
        db.session.commit()
        return "newchat created"
    elif request.form['chatName'] != None:
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
        logger.debug(i.chatname)
        returnQueryList.append({"chatname":i.chatname, "id":i.id})
    return jsonify(jsonList=returnQueryList)

#this function was propably for the old version
@app.route('/chatMessage', methods=['POST'])
@login_required
def addChatMessage():
    message = Message(request.form['message'], 1)
    db.session.add(message)
    db.session.commit()
    return "ok"

# joinChat:
# this function adds chat for the user and user for the chat in sql point of
# view.
@app.route("/joinChat", methods=['POST'])
@login_required
def joinChat():
    if request.form['chatID'] is None:
        return redirect(url_for('baseview'))
    user = User.query.filter_by(id=current_user.id).first()
    chatID = int(request.form['chatID'])
    chat = Chat.query.filter_by(id=chatID).first()
    user.chats.append(chat)
    return redirect(url_for('baseview'))
