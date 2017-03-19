# -*- coding: utf-8 -*-
"""
Created on Sun Mar 19 16:26:26 2017

@author: kankaan
"""

from flask_socketio import  send, disconnect, join_room, leave_room
from . import logger
from server import db, socketio
import datetime
import functools
from .models import  Message
from flask_login import current_user

# autenticated_only is for socket authentication.
# according to author of flask-socketio this kind of wrapped should be used
# with the flask-sockets.
# Check: https://flask-socketio.readthedocs.io/en/latest/
def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


@socketio.on('message')
@authenticated_only
def handle_message(message):
    logger.debug('received message: ' + message)

# messageJSON is used for broadcasting user messages to other chat members
# The method first creates message instance and saves it to database. Then
# method send it to the audience of the chat.
@socketio.on('JSONMessage')
@authenticated_only
def messageJSON(JSONMessage):
    now = datetime.datetime.now()
    timeNow = "(" + str(now.hour) + ":" + str(now.minute) + ") "
    m = Message(JSONMessage['message'], JSONMessage['room'], \
        current_user.id, now)
    message = timeNow + current_user.username + ": " + JSONMessage['message']
    db.session.add(m)
    db.session.commit()
    socketio.emit("receivedMessage", message, \
        room=JSONMessage['room'])


# Functions below are not propably needed.
@socketio.on('connect')
@authenticated_only
def on_connect():
    send('connected')

@socketio.on('join')
@authenticated_only
def on_join(data):
    room = data['room']
    join_room(room)
    send(' has entered the room.', room=room)

@socketio.on('leave')
@authenticated_only
def on_leave(data):
    room = data['room']
    leave_room(room)
    send(' has left the room.', room=room)
