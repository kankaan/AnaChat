#!flask/bin/python
from server import app, socketio

app.debug = True
#app.run(threaded=True)

socketio.run(app)

