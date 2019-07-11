import json, uuid, functools

from todoapi.db import get_db
from todoapi.utils import validate_signin, validate_signup

from flask import (
	request, g, Blueprint, abort
)

from werkzeug.security import generate_password_hash


bp = Blueprint('auth', __name__, url_prefix='/v1/auth')

# view for login(sign in and so on)
@bp.route('/signin', methods=('POST',))
def signin():
	db = get_db()

	# get form data and validate
	username = request.form.get('username', None)
	password = request.form.get('password', None)
	error = validate_signin(username, password)

	# set errors and return
	if error:
		return json.dumps({
			'result': 0,
			'error': error	
		})

	# if no errors, generate token, set it in DB and return it 
	user = db.execute(
			'SELECT id FROM user WHERE username = ?',
			(username,)
		).fetchone()
	token = str(uuid.uuid4())
	db.execute(
		'UPDATE user SET token = ? WHERE id = ?',
		(token, user['id'])
	)
	db.commit()
	return json.dumps({
		'result': 1,
		'token': token
	})

# view for register(sign up, create account and so on)
@bp.route('/signup', methods=('POST',))
def singup():
	db = get_db()

	username = request.form.get('username', None)
	password = request.form.get('password', None)
	repeated_password = request.form.get('repeated-password', None)
	error = validate_signup(username, password, repeated_password)

	if error:
		return json.dumps({
			'result': 0,
			'error': error	
		})

	db.execute(
		'INSERT INTO user (username, password) VALUES (?, ?)',
		(username, generate_password_hash(password))
	)
	db.commit()
	return json.dumps({
		'result': 1,
	})

# decorator for checking if there's token and if it's valid. then it write user to "g"
def valid_token_only(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		token = request.headers.get('token', None)	
		if token:
			db = get_db()
			user = db.execute(
				'SELECT * FROM user WHERE token = ?',
				(token,)
			).fetchone()
			if user:
				g.user = user
				return view(**kwargs)

		abort(403)
	return wrapped_view