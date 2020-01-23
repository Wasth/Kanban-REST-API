from todoapi.db import get_db
from werkzeug.security import check_password_hash


def validate_signin(username, password):
	error = None

	if not username:
		error = {
			'username': 'Username cannot be blank'
		}
	elif not password:
		error = {
			'password': 'Password cannot be blank'
		}
	else:
		db = get_db()
		user = db.execute(
			'SELECT * FROM user WHERE username = ?',
			(username,)
		).fetchone()

		if user is None or not check_password_hash(user['password'], password):
			error = {
				'password': 'Incorrect login or password'
			}
	return error


def validate_signup(username, password, repeated_password):
	error = None

	if not username:
		error = {
			'username': 'Username cannot be blank'
		}
	elif len(username) < 3:
		error = {
			'username': 'Username cannot be less than 3 symbols'
		}
	elif not password:
		error = {
			'password': 'Password cannot be blank'
		}
	elif len(password) < 6:
		error = {
			'password': 'Password cannot be less than 6 sybmols'
		}
	elif not repeated_password:
		error = {
			'repeated-password': 'Repeated password cannot be blank'
		}
	elif password != repeated_password:
		error = {
			'repeated-password': 'Repeated password shoud match'
		}
	else:
		db = get_db()
		if db.execute(
			'SELECT * FROM user WHERE username = ?', (username,)
			).fetchone():
			error = {
				'username': 'Username is already taken'
			}

	return error


def validate_board(name, color):
	error = None

	if not name:
		error = {
			'name': 'Board\'s name cannot be blank'
		}

	return error


def validate_list(name, sort):
	error = None

	if not name:
		error = {
			'name': 'Name of list cannot be blank'
		}
	elif sort and not sort.isdigit():
		error = {
			'sort': 'Sort must be integer'
		}
	return error


def validate_task(name):
	error = None

	if name is None:
		error = {
			'name': 'Name cannot be empty'
		}

	return error
