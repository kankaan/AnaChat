""" 
This is the SQL schema of the application.
"""

from flask_sqlalchemy import SQLAlchemy

from server import db, app
from flask_login import UserMixin
from passlib.apps import custom_app_context as pwd_context
from . import logger
import datetime

# Many to many relationship betweem User and Chat
userchat_table = db.Table('user_chat_table',
                          db.Column('user_id', db.Integer,
                                    db.ForeignKey('user.id'), nullable=False),
    db.Column('chat_id', db.Integer, db.ForeignKey('chat.id'), nullable=False),
    db.PrimaryKeyConstraint('user_id', 'chat_id'))

#user class for storing user information
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.String(128))
    jwt_token = db.Column(db.String)
    chats = db.relationship('Chat', secondary=userchat_table, backref='users')
    def __init__(self, username, password):
        self.username = username
        self.email = ""
        self.password_hash = pwd_context.encrypt(password)
    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=1000):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'id': self.id})

    def generate_auth_headers(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        headerToken = s.dumps({'id':self.id})
        authTokens.push(headerToken)
        #header = s.make_header({'token':headerToken})
        return header
        #return Response(headers=header)
        #return json.dumps(header)

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            print("saatu token: ", token)
            data = s.loads(token)
        except SignatureExpired:
            print("signaure expired")
            return None # valid token, but expired
        except BadSignature:
            print('badsigna')
            return None # invalid token
        user = User.query.get(data['id'])
        return user

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id) # python 3

# message table for storing users message data.
class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String)
    chat = db.Column(db.Integer, db.ForeignKey('chat.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    time = db.Column(db.DateTime)
    def __init__(self, message, chat, user, dTime=datetime.datetime.now()):
        self.message = message
        self.chat = chat
        self.user_id = user
        self.time = dTime

    def messageTime(self):
        return "(" + str(self.time.hour) + ":" + str(self.time.minute) + ")"

# Chat table:
# many to many with User table
# one to many with Message table
# Now Chat's description column isn't utilized
class Chat(db.Model):
    __tablename__ = 'chat'
    id = db.Column(db.Integer, primary_key=True)
    chatname = db.Column(db.String(80), unique=True)
    topic = db.Column(db.String)
    description = db.Column(db.String)
    messages = db.relationship('Message', backref='chatMessage', lazy='dynamic')

    def __init__(self, chatName, Topic, Description=""):
        self.chatname = chatName
        self.topic = Topic
        self.description = Description


def initDb():
    db.drop_all()
db.create_all()
