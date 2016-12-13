#!flask/bin/python
#import eventlet
#eventlet.monkey_patch()
from server import app, socketio

app.debug = True
#app.run(threaded=True)

socketio.run(app)

