import sqlalchemy
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Faculties(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'faculties'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    university_id = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    score = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
