from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.models import User, Post
import os
basedir = os.path.abspath(os.path.dirname(__file__))
from config import Config

class TestConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir,'unittest.db')


class UserModelCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app(TestConfig)
		self.app_contex = self.app.app_context()
		self.app_contex.push()
		# current_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'unittest.db')
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_contex.pop()

	def test_password_hashing(self):
		u = User(username='test1')
		u.set_password('cat')
		self.assertFalse(u.check_password('dog'))
		self.assertTrue(u.check_password('cat'))

	def test_follow(self):
		u1 = User(username='test1', email='test1@aa.com')
		u2 = User(username='test2', email='test2@aa.com')
		db.session.add(u1)
		db.session.add(u2)
		db.session.commit()
		self.assertEqual(u1.followed.all(),[])
		self.assertEqual(u2.followed.all(),[])

if __name__ == '__main__':
	unittest.main(verbosity=2)
