from flask_sqlalchemy import SQLAlchemy

from server import db
from server import app
from flask_login import UserMixin
from passlib.apps import custom_app_context as pwd_context


#user class for storing user information
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.String(128))
    jwt_token = db.Column(db.String)
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

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id) # python 3

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String)
    chat = db.relationship('Chat',backref='message',lazy='dynamic')
            

class Chat(db.Model):
    __tablename__ = 'chat'
    id = db.Column(db.Integer, primary_key=True)
    chatname = db.Column(db.String(80), unique=True)
    messages = db.Column(db.Integer, db.ForeignKey('message.id'))
        

def initDb():
    db.drop_all()
db.create_all()

