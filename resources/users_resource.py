from flask_restful import reqparse, abort, Resource
from flask import jsonify

from data.db_session import create_session
from data.users import User


parser = reqparse.RequestParser()
parser.add_argument('surname', type=str, required=True)
parser.add_argument('name', type=str, required=True)
parser.add_argument('email', type=str, required=True)
parser.add_argument('password', type=str, required=True)
parser.add_argument('address', type=str, required=True)
parser.add_argument('min_ege_score', type=int, required=True)


def abort_if_user_doesnt_exist(user_id):
    db_sess = create_session()
    user = db_sess.query(User).get(user_id)

    if not user:
        abort(404, message=f'Пользователь с ID = {user_id} не найден')

    return user, db_sess


class UsersResource(Resource):
    def get(self, user_id):
        user, _ = abort_if_user_doesnt_exist(user_id)
        return jsonify({'user': user.to_dict(only=(
            'id', 'surname', 'name', 'email', 'address', 'min_ege_score'
        ))})

    def delete(self, user_id):
        user, db_sess = abort_if_user_doesnt_exist(user_id)
        db_sess.delete(user)
        db_sess.commit()
        return jsonify({'message': 'Пользователь был удалён'})


class UsersListResource(Resource):
    def get(self):
        db_sess = create_session()
        users = db_sess.query(User).all()
        return jsonify({
            'users': [user.to_dict(only=('id', 'surname', 'name', 'email', 'address', 'min_ege_score'))
                      for user in users]
        })

    def post(self):
        args = parser.parse_args()
        db_sess = create_session()
        user = User()
        user.name = args['name']
        user.surname = args['surname']
        user.email = args['email']
        user.address = args['address']
        user.min_ege_score = args['min_ege_score']
        db_sess.add(user)
        db_sess.commit()

        return jsonify({'message': 'Пользователь был создан', 'id': user.id})
