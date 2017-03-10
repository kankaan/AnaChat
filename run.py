from server import app, socketio

app.debug = True
#app.run(threaded=True)
print("server will start")
print("default port is 5000")
socketio.run(app)
