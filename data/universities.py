import sqlalchemy
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship


class Universities(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'universities'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=False)
    address = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    deleted = sqlalchemy.Column(sqlalchemy.Boolean, default=False, nullable=False)
    faculties = relationship('Faculties')
    competitions = relationship('Competitions',
                                secondary='comp_to_university',
                                backref='universities')
