# AnAChat

AnaChat is a chat program, which includes server and client.
It is produced by Flask.

### Running

AnaChat is tested by Python 2.7 in Linux 3.14.27-100.fc19.x86_64 x86_64 environment.
Application uses Flask-Socketio for websockets.
According to author of Flask-socketio:
"Note that socketio.run(app) runs a production ready server when eventlet or
gevent are installed"
(http://flask-socketio.readthedocs.io/en/latest/)


### Backlog
* Failed login gives a failed login message to user, which username or password is incorrect
* Remove chat button. It should remove chat from joined chats list of the user
* Logo for the application
* Button to go from chat to user's frontpage
* Do more test cases
** stress test
