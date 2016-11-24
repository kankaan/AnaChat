from flask import Flask,request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class user:
	# class for user information
	def __init__(self):
		self.name = ""
		self.pwHash = ""
		self.chats = []

class userApi(Resource):
	def get(self):
		return "moi"

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


api.add_resource(userApi,'/')

if __name__ == '__main__':
	app.run(debug=True)
