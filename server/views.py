from flask import Flask,request, g,Response, render_template, flash, url_for,redirect, stream_with_context
from flask_login import LoginManager,login_user, logout_user, current_user, login_required
from urlparse import urlparse, urljoin
from forms import *
from server import app, db
import itertools
from server import login_manager
from models import *
import time

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
        print("foo")
        print(form.username.data)
        user = User.query.filter_by(username=form.username.data).first()
        print(user)
        if (user == None):
            return render_template('login.html',form=form)
        if (not user.verify_password(form.password.data)):
            return render_template('login.html',form=form)
        login_user(user)

        flash('Logged in successfully.')

        next = request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        if not is_safe_url(next):
            return flask.abort(400)

        return redirect(next or url_for('baseview'))
    print("!!!!!!!!!!!!!!!!")
    return render_template('login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('index.html')

@app.route('/')
@login_required
def index():
    return "Hello, %s!" % "ant"


@app.route('/register', methods=['GET', 'POST'])
def register():
    print("register")
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
	chatList = [{'chatName':'first chat'}]
	return render_template('userfrontpage.html', username=current_user.username,chatList=chatList)

@app.route('/chat',methods = ['GET','POST'])
@login_required
def chat():
	print("chat")
	messages = ["foo","bar"]
	chat = Chat.query.filter_by(id=1).first()
	print(chat.chatname)
	print(chat.messages)
	for i in chat.messages:
		print(i)
	return render_template('chat.html',rows=messages)

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


@app.route('/chatStream')
def streamMessages():
	if request.headers.get('accept') == 'text/event-stream':
		def generate():
			for i in range(10):
				yield "data: foo" #{"message":"mes","from":"another"}
				time.sleep(3)
		return Response(generate(),content_type="text/event-stream")
	return redirect('/chat')

@app.route('/stream')
def streamed_response():
    if request.headers.get('accept') == 'text/event-stream':
        def generate():
            for i, c in enumerate(itertools.cycle('\|/-')):
                yield "data: %s %d\n\n" % (c, i)
                time.sleep(4)  # an artificial delay   
        return Response(generate(),content_type='text/event-stream')
    return redirect(url_for('static', filename='index.html'))
