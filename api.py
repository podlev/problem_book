from flask import jsonify
from flask_restful import abort, Resource, reqparse

from data import db_session
from data.tasks import Task


def task_not_found(task_id):
    session = db_session.create_session()
    news = session.query(Task).get(task_id)
    if not news:
        abort(404, message=f"Task {task_id} not found")


class TasksResource(Resource):
    def get(self, task_id):
        task_not_found(task_id)
        session = db_session.create_session()
        task = session.query(Task).get(task_id)
        print(task.subject)
        return jsonify({'task': {'title': task.title, 'subject': task.subject, 'content': task.content,
                                 'rating': task.rating}})

    def delete(self, task_id):
        task_not_found(task_id)
        session = db_session.create_session()
        tasks = session.query(Task).get(task_id)
        session.delete(tasks)
        session.commit()
        return jsonify({'success': 'OK'})


class TasksListResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('title', required=True)
    parser.add_argument('content', required=True)
    parser.add_argument('subject', required=True)
    parser.add_argument('rating', required=True)

    def get(self):
        session = db_session.create_session()
        tasks = session.query(Task).all()
        print(tasks)
        return jsonify({'tasks': [{'title': task.title, 'subject': task.subject, 'content': task.content,
                                 'rating': task.rating} for task in tasks]})

    def post(self):
        args = reqparse.parse_args()
        session = db_session.create_session()
        tasks = Task(
            title=args['title'],
            content=args['content'],
            subject=args['subject'],
            rating=args['rating'],
        )
        session.add(tasks)
        session.commit()
        return jsonify({'success': 'OK'})
