import sqlalchemy
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


comp_to_university = sqlalchemy.Table(
    'comp_to_university',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('comp', sqlalchemy.Integer, sqlalchemy.ForeignKey('competitions.id')),
    sqlalchemy.Column('university', sqlalchemy.Integer, sqlalchemy.ForeignKey('universities.id'))
)


class Competitions(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'competitions'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=False)
