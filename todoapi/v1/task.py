import json

from .auth import valid_token_only
from todoapi.db import get_db
from todoapi.utils import validate_task

from flask import Blueprint, g, request, abort

bp = Blueprint('task', __name__, url_prefix='/v1/task')


@bp.route('/<int:list_id>', methods=('POST',))
@valid_token_only
def create(list_id):
	db = get_db()

	task = request.form.get('task', None)
	description = request.form.get('description', '')
	sort = request.form.get('sort', 0)
	color = request.form.get('color', '#fff')
	error = validate_task(task)

	if error:
		return json.dumps({
			'result': 0,
			'error': error
		})

	cursor = db.execute(
		'INSERT INTO task (task, description, sort, color, list_id) VALUES (?, ?, ?, ?, ?)',
		[task, description, sort, color, list_id]
	)

	db.commit()

	return json.dumps({
		'result': 1,
		'id': cursor.lastrowid
	})


@bp.route('/<int:task_id>', methods=['PUT'])
@valid_token_only
def update(task_id):
	if not is_author(task_id, g.user['id']):
		abort(403)

	db = get_db()
	task_obj = get_by_id(task_id)
	task = request.form.get('task', task_obj['task'])
	description = request.form.get('description', task_obj['description'])
	sort = request.form.get('sort', task_obj['sort'])
	color = request.form.get('color', task_obj['color'])

	db.execute(
		'UPDATE task SET task = ?, sort = ?, color = ?, description = ? WHERE id = ?',
		(task, sort, color, description, task_id)
	)
	db.commit()
	return json.dumps({
		'result': 1,
		'task': {
			'task': task,
			'description': description,
			'color': color,
			'sort': sort,
		}
	})


@bp.route('/<int:task_id>', methods=['DELETE'])
@valid_token_only
def delete(task_id):
	db = get_db()

	if not is_author(task_id, g.user['id']):
		abort(403)

	db.execute(
		'DELETE FROM task WHERE id = ?',
		(task_id,)
	)
	db.commit()

	return json.dumps({
		'result': 1,
		'id': task_id
	})


@bp.route('/<int:list_id>')
@valid_token_only
def index(list_id):
	db = get_db()
	tasks = db.execute('SELECT * FROM task WHERE list_id = ?', (list_id,)).fetchall()

	# shit code
	data = []
	for task in tasks:
		data.append({
			'id': task['id'],
			'task': task['task'],
			'description': task['description'],
			'color': task['color'],
			'sort': task['sort'],
		})

	return json.dumps({
		'result': 1,
		'tasks': data
	})


def get_by_id(task_id):
	db = get_db()
	return db.execute(
		'SELECT * FROM task t JOIN list l ON t.list_id == l.id JOIN board b ON b.id = l.board_id AND t.id = ?',
		(task_id,)
	).fetchone()


def is_author(task_id, user_id):
	task = get_by_id(task_id)
	return task['user_id'] == g.user['id']


@bp.after_request
def set_content_types(response):
	response.mimetype = 'application/json'
	response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, token')
	response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
	return response
