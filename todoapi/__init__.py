import os 

from flask import Flask
from . import db

def create_app():
	""" Creating flask app and return it """
	app = Flask(__name__)
	app.config.from_pyfile('config.py')

	# just for fun
	@app.route('/')
	def index():
		return '<h2>This is not site</h2><h1>However, hello world!</h1>';

	db.register_init_db(app)

	from todoapi.v1 import auth, board
	app.register_blueprint(auth.bp)
	app.register_blueprint(board.bp)


	return app