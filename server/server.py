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

#Let's crete the app
app = Flask(__name__)
app.debug = True
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
auth = HTTPTokenAuth('Bearer')
#configuration should be moved to different file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///anaChat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = os.urandom(24) 
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)

import models
import views
authTokens = []

@auth.verify_token
def verify_token(token):
	print("VERIVDYFYFDSAFFAAFAS")
	print(token)
	print(token)
	g.user = None
	try:
		data = jwt.loads(token)
	except:
		return False
	user = User.query(jwtToken=token).first()
	if user == None:
		return False
	return True

def tokenLogin(message):
	def decorated(*args, **kwargs):
		print(message)
	return message

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



@app.route('/')
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

class logout(Resource):
	def post(self):
		args = parser.parse_args()
		token = args['token']
		if token in authTokens: authTokens.remove(token)
		return "Logout"

api.add_resource(loginApi, '/api/login/')
api.add_resource(logout, '/api/logout/')
api.add_resource(userApi,'/api/user/')
api.add_resource(chatAPI, '/api/chat/')

if __name__ == '__main__':
	app.run(debug=True)
