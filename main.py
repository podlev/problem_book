import os
from flask import Flask, render_template, redirect, request, make_response, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.exceptions import abort
from flask_restful import reqparse, abort, Api, Resource
from data import db_session
from data.solves import Solve
from data.tasks import Task
from data.users import User
from edit_solve import SolveForm
from registration import RegisterForm, LoginForm
from edit_tasks import TaskForm
from api import TasksResource, TasksListResource

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = '0YvRhNC/0YvQstGE0YvQutGD0YTRhg=='


def main():
    api.add_resource(TasksListResource, '/api/v2/tasks')
    api.add_resource(TasksResource, '/api/v2/tasks/<int:task_id>')
    db_session.global_init("db/python_tasks.sqlite")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port)
    # app.run(host='0.0.0.0', port=port)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route("/")
@app.route('/index')
def index():
    session = db_session.create_session()
    result = session.query(Task)[:-4:-1]
    return render_template("home_page.html", title='Главная страница', tasks=result)


@app.route('/about')
def about():
    return render_template("about_page.html", title='О проекте')


@app.route('/registration', methods=['GET', 'POST'])
def reqistration():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('registration_page.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('registration_page.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('registration_page.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login_page.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login_page.html', title='Авторизация', form=form)


@app.route('/subjects', methods=['GET', 'POST'])
def subject():
    session = db_session.create_session()
    subjects = session.query(Task).all()
    result = dict()
    for i in subjects:
        if i.subject not in result:
            result[i.subject] = 1
        else:
            result[i.subject] += 1
    return render_template('subjects_page.html', title='Список тем', subjects=result.items())


@app.route('/subjects/tasks/<string:topic>', methods=['GET', 'POST'])
def tasks(topic):
    if topic == 'all':
        session = db_session.create_session()
        result = session.query(Task).all()
    else:
        session = db_session.create_session()
        result = session.query(Task).filter(Task.subject == topic).all()
    return render_template('tasks_page.html', title='Список задач', tasks=result)


@app.route('/tasks/<int:id>', methods=['GET', 'POST'])
def view_task(id):
    session = db_session.create_session()
    result = session.query(Task).filter(Task.id == id).first()
    return render_template('view_page.html', title=f'Задача «{result.title}»', task=result)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def my_tasks():
    session = db_session.create_session()
    result = session.query(Task)
    return render_template('edit_page.html', title='Мои задачи', tasks=result)


@app.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        task = Task()
        task.title = form.title.data
        task.content = form.content.data
        task.subject = form.subject.data
        task.rating = form.rating.data
        current_user.task.append(task)
        session.merge(current_user)
        session.commit()
        return redirect('/edit')
    return render_template('task_page.html', title='Добавить задачу', form=form)


@app.route('/task_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    form = TaskForm()

    if request.method == "GET":
        session = db_session.create_session()
        task = session.query(Task).filter(Task.id == id, current_user.role == 'admin').first()
        if task:
            form.title.data = task.title
            form.content.data = task.content
            form.rating.data = task.rating
            form.subject.data = task.subject
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        task = session.query(Task).filter(Task.id == id, current_user.role == 'admin').first()
        if task:
            task.title = form.title.data
            task.content = form.content.data
            task.rating = form.rating.data
            task.subject = form.subject.data
            session.commit()
            return redirect(f'/tasks/{task.id}')
        else:
            abort(404)
    return render_template('task_page.html', title='Редактирование задачи', form=form)


@app.route('/task_delete/<int:id>')
@login_required
def news_delete(id):
    session = db_session.create_session()
    task = session.query(Task).filter(Task.id == id).first()
    if task:
        session.delete(task)
        session.commit()
    else:
        abort(404)
    return redirect('/edit')


@app.route('/users_page', methods=['GET', 'POST'])
@login_required
def users():
    session = db_session.create_session()
    result = session.query(User)
    return render_template('users_page.html', title='Пользователи', items=result)


@app.route('/change_role/<int:id>', methods=['GET', 'POST'])
@login_required
def change_role(id):
    session = db_session.create_session()
    result = session.query(User).filter(User.id == id).first()
    if result.role == 'user':
        result.role = 'admin'
    else:
        result.role = 'user'
    session = db_session.create_session()
    session.merge(result)
    session.commit()
    return redirect('/users_page')


@app.route('/user_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def user_delete(id):
    session = db_session.create_session()
    user = session.query(User).filter(User.id == id).first()
    if user:
        session.delete(user)
        session.commit()
    else:
        abort(404)
    return redirect('/users_page')


@app.route('/solves')
@login_required
def solves():
    session = db_session.create_session()
    result = session.query(Solve).filter((Solve.user == current_user) | (current_user.role == 'admin')).all()
    if current_user.role == 'admin':
        return render_template('admin_solves_page.html', title='Мои решения', solves=result)
    else:
        return render_template('solves_page.html', title='Мои решения', solves=result)


@app.route('/add_solve/<int:task_id>', methods=['GET', 'POST'])
@login_required
def add_solve(task_id):
    form = SolveForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        solve = Solve()
        solve.content = form.content.data
        solve.user = current_user
        solve.task_id = task_id
        session.merge(solve)
        session.commit()
        return redirect(f'/tasks/{solve.task_id}')
    return render_template('solve_page.html', title='Добавить задачу', form=form)


@app.route('/solve_delete/<int:id>')
@login_required
def solve_delete(id):
    session = db_session.create_session()
    solve = session.query(Solve).filter(Solve.id == id).first()
    if solve:
        session.delete(solve)
        session.commit()
    else:
        abort(404)
    return redirect('/solves')


@app.route('/change_solve_status/<int:id>')
@login_required
def cchange_solve_status(id):
    session = db_session.create_session()
    result = session.query(Solve).filter(Solve.id == id).first()
    result.accept = not result.accept
    session = db_session.create_session()
    session.merge(result)
    session.commit()
    return redirect('/solves')


if __name__ == '__main__':
    main()
