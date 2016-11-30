import os
from flask import Flask,request, g,Response, render_template
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (JSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from itsdangerous import TimedJSONWebSignatureSerializer as JWT
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask_login import LoginManager,login_user, logout_user, current_user, login_required
import json
from forms import *
from flask_wtf.csrf import CsrfProtect

#Let's crete the app
app = Flask(__name__)
app.debug = True
api = Api(app)
CsrfProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
auth = HTTPTokenAuth('Bearer')
#configuration should be moved to different file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///anaChat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = os.urandom(24) 
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)

#from models import *
import models
import views

response_headers = {'Content-type':'application/json'}
# reqparser from flask_restful
parser = reqparse.RequestParser()
parser.add_argument('message')
parser.add_argument('username')
parser.add_argument('password')
parser.add_argument('token',location='headers')

# API class for user
# Post will create new user
class userApi(Resource):
	def get(self):
		print("/api/Chat/")
		return {"user":"userGetBack"}, 200, response_headers
	#def post(lf, userFuntion):
	def post(self):
		args = parser.parse_args()
		print(args['username'])
		print(args['password'])
		if (User.query.filter_by(username=args['username']).first() == None):
			newUser = User(args['username'],args['password'])
			db.session.add(newUser)
			db.session.commit()
			return "user added"
		else:
			return "user was there already"


@app.route('/register', methods=['GET', 'POST'])
def register():
    print("register")
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data, form.email.data,
                    form.password.data)
        db_session.add(user)
        flash('Thanks for registering')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

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

        flask.flash('Logged in successfully.')

        next = flask.request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        if not is_safe_url(next):
            return flask.abort(400)

        return flask.redirect(next or flask.url_for('index'))
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

# API for chat:
# Chat handles messages
class chatAPI(Resource):
	def get(self):
		newChat = Chat()
		db.session.add(chat)
		db.session.commit()
		return newChat
	def post(self,chatName):
		args = parser.parse_args()
		print("cat ",chatName)
		print("post: ",args['message'])
		chatY[chatName] = args['message']
		return {chatName:chatY[chatName]}

class loginApi(Resource):
	#@auth.verify_token
	def post(self):
		print("TESTTSTOTOTOOTOTOSTTI")
		args = parser.parse_args()
		print("kayttaja ",args['username'])
		print("salasana ",args['password'])
		user = User.query.filter_by(username = args['username']).first()
		if (not user or not user.verify_password(args['password'])):
			return False
		token = user.generate_auth_token()	
		authTokens.append((token,user))
		user.jwtToken = token
		g.user = user
		return True,200, {"Authorization": token}

	def get(self):
		token = g.user.generate_auth_token(600)
		return jsonify({'token': token.decode('ascii'), 'duration': 600})	

class logoutApi(Resource):
	def post(self):
		args = parser.parse_args()
		token = args['token']
		if token in authTokens: authTokens.remove(token)
		return "Logout"

api.add_resource(loginApi, '/api/login/')
api.add_resource(logoutApi, '/api/logout/')
api.add_resource(userApi,'/api/user/')
api.add_resource(chatAPI, '/api/chat/')

def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        #url = url_for(rule.endpoint, **options)
        line = urllib.unquote("{:50s} {:20s}".format(rule.endpoint, methods))
        output.append(line)
    
    for line in sorted(output):
        print line

if __name__ == '__main__':
	list_routes()
	app.run(debug=True)
