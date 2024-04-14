import flask
from flask import jsonify, request, make_response

import datetime

from data.db_session import create_session
from data.users import User

import hashlib

sha256_hash = hashlib.new('sha256')

blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/users')
def get_all_users():
    db_sess = create_session()
    users = db_sess.query(User).all()

    return jsonify(
        {
            'users':
                [item.to_dict(only=('id', 'surname', 'name', 'address', 'email', 'min_ege_score', 'type'))
                 for item in users]
        }
    )


@blueprint.route('/api/users/<int:user_id>')
def get_user_by_id(user_id: int):
    db_sess = create_session()
    user = db_sess.query(User).get(user_id)

    if not user:
        return make_response(jsonify({'error': f'Пользователя с ID = {user_id} не существует'}), 404)

    return jsonify(
        user.to_dict(only=('id', 'surname', 'name', 'address', 'email', 'min_ege_score', 'type'))
    )


@blueprint.route('/api/users', methods=['POST'])
def create_user():
    if not request.json:
        return make_response(jsonify({'error': 'Отсутствуют аргументы'}), 400)
    elif not all(key in request.json
                 for key in ['id', 'surname', 'name', 'address', 'email', 'min_ege_score']):
        return make_response(jsonify({'error': 'Bad request'}), 400)

    db_sess = create_session()
    user = User()
    user.name = request.json['name']
    user.surname = request.json['surname']
    sha256_hash.update(request.json['password'].encode())
    user.hashed_password = sha256_hash.hexdigest()
    user.address = request.json['address']
    user.email = request.json['email']
    user.min_ege_score = request.json['min_ege_score']
    user.type = 2
    user.modified_date = datetime.datetime.now()
    db_sess.add(user)
    db_sess.commit()

    return make_response({'id': user.id, 'message': 'Пользователь был успешно создан'}, 200)


@blueprint.route('/api/users/<int:user_id>', methods=['PUT'])
def edit_user(user_id: int):
    db_sess = create_session()
    user = db_sess.query(User).get(user_id)

    if not user:
        return make_response(jsonify({'error': 'Пользователь не был найден'}), 404)
    elif not request.json:
        return make_response(jsonify({'error': 'Пустой запрос'}), 400)
    elif not all(key in ['id', 'surname', 'name', 'address', 'email', 'min_ege_score']
                 for key in request.json):
        return make_response(jsonify({'error': 'Bad request'}), 400)

    for key in request.json:
        if key == 'surname':
            user.surname = request.json[key]
        elif key == 'name':
            user.name = request.json[key]
        elif key == 'address':
            user.address = request.json[key]
        elif key == 'email':
            user.email = request.json[key]
        elif key == 'min_ege_score':
            user.min_ege_score = request.json[key]

    db_sess.add(user)
    db_sess.commit()

    return make_response(jsonify({'message': 'Изменения прошли успешно'}), 200)


@blueprint.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db_sess = create_session()
    user = db_sess.query(User).get(user_id)

    if not user:
        return make_response(jsonify({'error': 'User not found'}, 404))

    db_sess.delete(user)
    db_sess.commit()

    return make_response(jsonify({'message': 'Пользователь был успешно удалён'}), 200)
