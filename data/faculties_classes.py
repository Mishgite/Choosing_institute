import sqlalchemy
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Faculties_classes(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'faculties_classes'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    faculty_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    class_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
