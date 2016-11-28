import requests
import os
import unittest
import tempfile
import server

class UserTest(unittest.TestCase):
	def setUp(self):
		self.db_fd, server.app.config['SQLALCHEMY_DATABASE_URI'] = \
			tempfile.mkstemp()
		server.app.config['TESTING'] = True
		self.app = server.app.test_client()
		
	def tearDown(self):
		os.close(self.db_fd)
		os.unlink( server.app.config['SQLALCHEMY_DATABASE_URI'])

	def addNewUser(self,user,pw):
		return self.app.post("/user", data= dict(
			userName=user,
			pWord=pw))

	def test_moi(self):
		rv = self.app.get("/user")
		with  open("debug.txt","w") as t:
			t.write(i)
		assert "moi" in "moi"

	def test_AddNewUser(self):
		rv = self.addNewUser('TimoTestaaja',"cryptedPW")
		#assert b"user added" in rv.data

if __name__ == "__main__":
	unittest.main()
