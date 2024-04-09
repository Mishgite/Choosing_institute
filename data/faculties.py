import sqlalchemy as sa
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from data.classes import Classes


class Faculties(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'faculties'

    id = sa.Column(sa.Integer,
                           primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    university_id = sa.Column(sa.String, sa.ForeignKey('universities.id'), nullable=False)
    score = sa.Column(sa.Integer, nullable=True)
    fclasses = relationship(Classes, secondary='faculties_classes')
