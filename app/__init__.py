from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
from flask_bootstrap import Bootstrap

import logging
from logging.handlers import RotatingFileHandler
import os, time

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
moment = Moment()
bootstrap = Bootstrap()

def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(config_class)

	# model registration
	db.init_app(app)
	migrate.init_app(app, db)
	login.init_app(app)
	moment.init_app(app)
	bootstrap.init_app(app)

	# blue print registration
	from app.errors import bp as errors_bp
	app.register_blueprint(errors_bp)
	from app.auth import bp as auth_bp
	app.register_blueprint(auth_bp)
	from app.main import bp as main_bp
	app.register_blueprint(main_bp)
	from app.api import bp as api_bp
	app.register_blueprint(api_bp)
	from app.admin import bp as admin
	app.register_blueprint(admin)

	# log
	if not app.debug:
		if not os.path.exists('logs'):
			os.mkdir('logs')

		server_handler = RotatingFileHandler('logs/logs.log', maxBytes=10240, backupCount=10)
		# file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s '))
		server_handler.setFormatter(
			logging.Formatter('********\n%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
		server_handler.setLevel(logging.INFO)

		error_handler = RotatingFileHandler('logs/error.log', maxBytes=10240, backupCount=10)
		error_handler.setFormatter(logging.Formatter('#########\n%(asctime)s %(levelname)s: %(message)s'))
		# server_handler.setLevel(logging.DEBUG)
		error_handler.setLevel(logging.ERROR)

		app.logger.addHandler(error_handler)
		app.logger.addHandler(server_handler)
		app.logger.setLevel(logging.DEBUG)
		app.logger.info('Microblog startup')

	return app


