import os
from flask import Flask,request, g,Response
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (JSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
import json

#Let's crete the app
app = Flask(__name__)
app.debug = True
api = Api(app)
#configuration should be moved to different file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///anaChat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = os.urandom(24) 
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)
'''
class Tokens(db.Model):
	__table__ = 'Tokens'
	id = db.Column(db.Integer, primary_key=True)
	token = db.Column(db.String)
	def __init__(self,token):
		self.token = token
'''
authTokens = []

#user class for storing user information
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.String(128))
    def __init__(self, username, password):
        self.username = username
        self.email = ""
        self.password_hash = pwd_context.encrypt(password)
    
    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)
	
    def generate_auth_token(self, expiration = 1000):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({ 'id': self.id })
	
    def generate_auth_headers(self,expiration =600):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        headerToken = s.dumps({'id':self.id})
        authTokens.push(headerToken)
        #header = s.make_header({'token':headerToken})
        return header
        #return Response(headers=header)
        #return json.dumps(header)

    @staticmethod
    def verify_auth_token( token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            print("saatu token: ",token)
            data = s.loads(token)
        except SignatureExpired:
            print("signaure expired")
            return None # valid token, but expired
        except BadSignature:
            print('badsigna')
            return None # invalid token
        user = User.query.get(data['id'])
        return user

db.create_all()

# reqparser from flask_restful
parser = reqparse.RequestParser()
parser.add_argument('message')
parser.add_argument('username')
parser.add_argument('password')
parser.add_argument('token',location='headers')

def loginDecorate(auth):
	def token(*args, **kwargs):
		#check the users token here and return the function
		args = parser.parse_args()
		print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		if (args['token'] == None):
			return "not authenticated"
		print("token ", args['token'])
		print("user: ",User.verify_auth_token(args['token']))
		if (User.verify_auth_token(args['token']) == None):
			return "false"
		return auth
	return token

# API class for user
# Post will create new user
class userApi(Resource):
	@loginDecorate
	def get(self):
		return {'resp':"True user"}
	#def post(self, userFuntion):
	def post(self):
		args = parser.parse_args()
		print(args['userName'])
		print(args['pWord'])
		if (User.query.filter_by(username=args['userName']).first() == None):
			newUser = User(args['userName'],args['pWord'])
			db.session.add(newUser)
			db.session.commit()
			return "user added"
		else:
			return "user was there already"



class chat:
	# chat object
	def __init__(self):
		self.name = ""
		self.users = []
		self.messages = []

	def addMessage(self,message):
		self.messages.push(message)

	def readMessages(self):
		return self.messages

chatY = {}
# API for chat:
# Chat handles messages
class chatAPI(Resource):
	def get(self):
		return chaty
	def post(self,chatName):
		args = parser.parse_args()
		print("cat ",chatName)
		print("post: ",args['message'])
		chatY[chatName] = args['message']
		return {chatName:chatY[chatName]}

class login(Resource):
	def post(self):
		args = parser.parse_args()
		print("kayttaja ",args['username'])
		print("salasana ",args['password'])
		user = User.query.filter_by(username = args['username']).first()
		if (not user or not user.verify_password(args['password'])):
			return False
		token = user.generate_auth_token()	
		authTokens.append(token)
		return {"token":token}

	def get(self):
		token = g.user.generate_auth_token(600)
		return jsonify({'token': token.decode('ascii'), 'duration': 600})	

class logout(Resource):
	def post(self):
		args = parser.parse_args()
		token = args['token']
		if token in authTokens: authTokens.remove(token)
		return "Logout"

api.add_resource(login, '/api/login/')
api.add_resource(logout, '/api/logout/')
api.add_resource(userApi,'/api/user/')
api.add_resource(chatAPI, '/api/chat/<string:chatName>')

if __name__ == '__main__':
	app.run(debug=True)
