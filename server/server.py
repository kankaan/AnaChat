from flask import Flask,request
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy
#import models

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///anaChat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    #email = db.Column(db.String(120), unique=True)
    def __init__(self, username):
        self.username = username
        self.email = ""
    def __repr__(self):
        return '<User %r>' % self.username


db.create_all()
parser = reqparse.RequestParser()
parser.add_argument('message')
parser.add_argument('userName')

# API class for user
# Post will create new user
class userApi(Resource):
	def get(self):
		return "moi"
	#def post(self, userFuntion):
	def post(self):
		args = parser.parse_args()
		print(args['userName'])
		if (User.query.filter_by(username=args['userName']).first() == None):
			newUser = User(args['userName'])
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
		self.messges = []

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

api.add_resource(userApi,'/user/')
api.add_resource(chatAPI, '/chat/<string:chatName>')

if __name__ == '__main__':
	app.run(debug=True)
