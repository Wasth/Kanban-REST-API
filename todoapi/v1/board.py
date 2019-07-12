import json

from .auth import valid_token_only
from todoapi.db import get_db
from todoapi.utils import validate_board

from flask import (
	request, g, Blueprint, abort
)


bp = Blueprint('board', __name__, url_prefix='/v1/board')


@bp.route('/<int:board_id>', methods=('PUT',))
@bp.route('/', methods=('POST',))
@valid_token_only
def create_or_update(board_id=None):
	db = get_db()

	name = request.form.get('name', None)
	color = request.form.get('color', None)
	error = validate_board(name, color)

	if error:
		return json.dumps({
			'result': 0,
			'error': error	
		})

	myresponse = {
		'result': 1
	}

	if request.method == 'POST':
		added_id = add_board(name, color)
		myresponse.update(id=added_id)
	elif request.method == 'PUT':
		if color is None:
			color = get_by_id(board_id)['color']
		update(board_id, name, color)
		myresponse.update(board = {
			'name': name,
			'color': color	
		})

	db.commit()

	return json.dumps(myresponse)


@bp.route('/<int:board_id>', methods=['DELETE'])
@valid_token_only
def delete(board_id):
	db = get_db()

	if not is_author(board_id, g.user['id']):
		abort(403)

	db.execute(
		'DELETE FROM board WHERE id = ?',
		(board_id,)
	)
	db.commit()

	return json.dumps({
		'result': 1,
		'id': board_id
	})

@bp.route('/')
@valid_token_only
def index():
	db = get_db()
	boards = get_by_user(g.user['id'])
	
	# shit code
	data = []
	for board in boards:
		data.append({
			'id': board['id'],	
			'name': board['name'],	
			'color': board['color'],	
		})

	return json.dumps({
		'result': 1,
		'boards': data	
	})

def get_by_id(board_id):
	db = get_db()
	return db.execute('SELECT * FROM board WHERE id = ?', [board_id]).fetchone()

def is_author(board_id, user_id):
	board = Board.get_by_id(board_id)
	return user_id == board['user_id']

def get_by_user(user_id):
	db = get_db()
	return db.execute('SELECT * FROM board WHERE user_id = ?', (user_id,)).fetchall()

def add_board(name, color):
	db = get_db()
	cursor = db.execute(
		'INSERT INTO board (name, color, user_id) VALUES (?, ?, ?)',
		(name, color, g.user['id'])
	)
	db.commit()
	return cursor.lastrowid

def update(board_id, name, color)
	db.execute(
		'UPDATE board SET name = ?, color = ? WHERE id = ?',
		(name, color, board_id)
	)