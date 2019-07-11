import json

from .auth import valid_token_only
from todoapi.db import get_db
from todoapi.utils import validate_board

from flask import (
	request, g, Blueprint, abort
)


bp = Blueprint('board', __name__, url_prefix='/v1/board')

# creating without int:board_id
@bp.route('/<int:board_id>', methods=('PUT',))
@bp.route('/', methods=('POST',))
@valid_token_only
def create_or_update(board_id=None):
	db = get_db()

	name = request.form.get('name', None)
	color = request.form.get('color', '#FFF')
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
		cursor = db.execute(
			'INSERT INTO board (name, color, user_id) VALUES (?, ?, ?)',
			(name, color, g.user['id'])
		)
		myresponse.update(id=cursor.lastrowid)
	elif request.method == 'PUT':
		if board_id is None: 
			abort(404)
		db.execute(
			'UPDATE board SET name = ?, color = ? WHERE id = ?',
			(name, color, board_id)
		)
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

	board = db.execute(
		'SELECT * FROM board WHERE id = ?',
		(board_id,)
	).fetchone()

	if board['user_id'] != g.user['id']	:
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
	boards = db.execute('SELECT * FROM board WHERE user_id = ?', (g.user['id'],)).fetchall()
	
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
