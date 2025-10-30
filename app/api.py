from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource
from flask_login import login_required, current_user
from . import db
from .models import Task, User

bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(bp)

class TaskList(Resource):
    @login_required
    def get(self):
        tasks = Task.query.filter_by(owner=current_user).all()
        return jsonify([{'id': t.id, 'title': t.title, 'done': t.done}])

    @login_required
    def post(self):
        data = request.get_json(force=True)
        title = data.get('title', '').strip()
        if not title:
            return jsonify({'error': 'Title required'}), 400
        t = Task(title=title, owner=current_user)
        db.session.add(t)
        db.session.commit()
        return jsonify({'id': t.id, 'title': t.title, 'done': t.done}), 201

class TaskRes(Resource):
    @login_required
    def put(self, task_id):
        t = Task.query.filter_by(id=task_id, owner=current_user).first_or_404()
        t.done = not t.done
        db.session.commit()
        return jsonify({'id': t.id, 'done': t.done})

    @login_required
    def delete(self, task_id):
        t = Task.query.filter_by(id=task_id, owner=current_user).first_or_404()
        db.session.delete(t)
        db.session.commit()
        return '', 204

api.add_resource(TaskList, '/tasks')
api.add_resource(TaskRes,  '/tasks/<int:task_id>')