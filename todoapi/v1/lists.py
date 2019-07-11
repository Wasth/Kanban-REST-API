import json

from .auth import valid_token_only
from todoapi.db import get_db
from todoapi.utils import validate_list

from flask import Blueprint, g, request, abort 

bp = Blueprint('list', __name__, url_prefix='/v1/list')

@bp.route('/<int:list_id>', methods=('PUT',))
@bp.route('/<int:board_id>', methods=('POST',))
@valid_token_only
def create_or_update(list_id=None, board_id=None):
	db = get_db()

	name = request.form.get('name', None)
	sort = request.form.get('sort', 0)
	error = validate_list(name, sort)

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
			'INSERT INTO list (name, sort, board_id) VALUES (?, ?, ?)',
			(name, sort, board_id)
		)
		myresponse.update(id=cursor.lastrowid)
	elif request.method == 'PUT':
		if list_id is None: 
			abort(404)
		sort = db.execute('SELECT sort FROM list WHERE id = ?', (list_id,)).fetchone()['sort']
		db.execute(
			'UPDATE list SET name = ?, sort = ? WHERE id = ?',
			(name, sort, list_id)
		)
		myresponse.update(board = {
			'name': name,
			'sort': sort	
		})

	db.commit()

	return json.dumps(myresponse)


@bp.route('/<int:list_id>', methods=['DELETE'])
@valid_token_only
def delete(list_id):
	db = get_db()

	list_obj = db.execute(
		'SELECT * FROM list WHERE id = ?',
		(list_id,)
	).fetchone()

	board = db.execute(
		'SELECT * FROM board WHERE id = ?',
		(list_obj['board_id'],)
	).fetchone()

	if board['user_id'] != g.user['id']	:
		abort(403)

	db.execute(
		'DELETE FROM list WHERE id = ?',
		(list_id,)
	)
	db.commit()

	return json.dumps({
		'result': 1,
		'id': list_id
	})

@bp.route('/<int:board_id>')
@valid_token_only
def index(board_id):
	db = get_db()
	lists = db.execute('SELECT * FROM list WHERE board_id = ?', (board_id,)).fetchall()
	
	# shit code
	data = []
	for list_obj in lists:
		data.append({
			'id': list_obj['id'],	
			'name': list_obj['name'],	
			'sort': list_obj['sort'],	
		})

	return json.dumps({
		'result': 1,
		'lists': data	
	})