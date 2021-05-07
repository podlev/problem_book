from flask import jsonify
from flask_restful import Resource, reqparse, abort

from data import db_session
from data.tasks import Task

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('subject', required=True)
parser.add_argument('rating', required=True)

def task_not_found(task_id):
    session = db_session.create_session()
    task = session.query(Task).get(task_id)
    if not task:
        abort(404, message=f"Task {task_id} not found")


class TasksResource(Resource):
    def get(self, task_id):
        task_not_found(task_id)
        session = db_session.create_session()
        task = session.query(Task).get(task_id)
        return jsonify({'task': task.to_dict(only=('id', 'title', 'content', 'subject', 'rating', 'created_date'))})

    def delete(self, task_id):
        task_not_found(task_id)
        session = db_session.create_session()
        tasks = session.query(Task).get(task_id)
        session.delete(tasks)
        session.commit()
        return jsonify({'success': 'OK'})


class TasksListResource(Resource):
    def get(self):
        session = db_session.create_session()
        tasks = session.query(Task).all()
        return jsonify({'tasks': [item.to_dict(
            only=('id', 'title', 'content', 'subject', 'rating', 'created_date')) for item in tasks]})

    def post(self):
        args = reqparse.parse_args()
        session = db_session.create_session()
        task = Task(
            title=args['title'],
            content=args['content'],
            subject=args['subject'],
            rating=args['rating'],
        )
        session.add(task)
        session.commit()
        return jsonify({'success': 'OK'})
