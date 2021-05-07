import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Solve(SqlAlchemyBase):
    __tablename__ = 'solves'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=True)
    task_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("tasks.id"), nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    accept = sqlalchemy.Column(sqlalchemy.BOOLEAN, default=False)
    created_date = sqlalchemy.Column(sqlalchemy.Date, default=datetime.date.today)
    user = orm.relation('User', back_populates='solve')
    task = orm.relation('Task', back_populates='solve')

    def __repr__(self):
        return f'Решение: {self.id}, {self.user_id}, {self.task_id}, {self.content}, {self.accept}'
