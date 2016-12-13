# AnAChat

AnaChat is a chat server.
It is produced by Flask.

### Running

AnaChat works in Python 2.7. 
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
* picture sending feature
** minimize picture
** send picure to user, who wants to download it
* Windows phone and Android application
* Create better README file
