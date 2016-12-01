#init
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
app.config.from_object('config')
app.debug = True
api = Api(app)
CsrfProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
db = SQLAlchemy(app)


from server import views, models
