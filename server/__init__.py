#initialization of the app.
import os
from flask import Flask, request, g,Response, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (JSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from itsdangerous import TimedJSONWebSignatureSerializer as JWT
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO


#Let's crete the app
app = Flask(__name__)
app.config.from_object('config')
app.debug = True
csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
db = SQLAlchemy(app)
socketio = SocketIO(app)

from server import views, models
