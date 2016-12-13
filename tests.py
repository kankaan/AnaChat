import os
import unittest
import coverage
import tempfile
#import flaskr
#from flask import test_client

from server import app, db
from server.models import User

cov = coverage.coverage(branch=True)
cov.start()

class TestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		dir_path = os.path.dirname(os.path.realpath(__file__))
		app.config['SQLALCHEMY_DATABASE_URI'] =  'sqlite:///' + os.path.join(dir_path, 'test.db')
		self.app = app.test_client()
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	def login(self,username,password):
		return self.app.post('login',data=dict(
			username=username,
			password=password),
			follow_redirects=True)

	def logout(self):
		return self.app.get('logout')
	
	def register(self,username,password,email="test@test.com"):
		return self.app.post('register',data=dict(username=username,
			password=password,email=email,confirm=password), 
			follow_redirects=True)

	def test_resource_not_allowed(self):
		rv = self.app.post('baseview',follow_redirects=True)
		assert rv.status_code == 400

	def test_login(self):
		rv = self.login("tester","password")
		assert rv.status_code == 400

	def test_register(self):
		rv =self.register("testPerson","testpass")
		assert rv.status_code == 200
		# trying to register again with the same name
		rv = self.register("testPerson","testpass")
		assert rv.status_code == 400

if __name__ == '__main__':
    unittest.main()
