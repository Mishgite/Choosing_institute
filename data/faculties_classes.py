import sqlalchemy as sa
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Faculties_classes(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'faculties_classes'

    id = sa.Column(sa.Integer,
                           primary_key=True, autoincrement=True)
    faculty_id = sa.Column(sa.Integer, sa.ForeignKey('faculties.id'), nullable=False)
    class_id = sa.Column(sa.Integer, sa.ForeignKey('classes.id'), nullable=False)
