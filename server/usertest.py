import requests
import unittest
import tempfile
import server
#import server
# configurate common url for tests
url = "http://127.0.0.1:5000/"
urlUser = ""

class UserTest(unittest.TestCase):
	def setUp(self):
		self.db_fd, app.config['SQLALCHEMY_DATABASE_URI'] = tempfile.mkstemp()
		server.app.config['TESTING'] = True
		self.app = server.app.test_client()
		
	def tearDown(self):
		os.close(self.db_fd)
		os.unlink( app.config['SQLALCHEMY_DATABASE_URI'])

	def addNewUser(self):
		return self.app.post("/user", data= dict(
			userName='newUser',
			pWord='password'))


if __name__ == "__main__":
	unittest.main()
