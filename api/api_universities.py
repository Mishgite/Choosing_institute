import flask
from flask import jsonify, request, make_response

from data.db_session import create_session
from data.universities import Universities

import hashlib

sha256_hash = hashlib.new('sha256')

blueprint = flask.Blueprint(
    'universities_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/universities')
def get_all_universities():
    db_sess = create_session()
    universities = db_sess.query(Universities).all()

    return jsonify(
        {
            'universities':
                [item.to_dict()
                 for item in universities]
        }
    )


@blueprint.route('/api/universities/<int:university_id>')
def get_university_by_id(university_id: int):
    db_sess = create_session()
    university = db_sess.query(Universities).get(university_id)

    if not university:
        return make_response(jsonify({'error': f'Университет с ID = {university_id} не существует'}), 404)

    return jsonify(
        university.to_dict()
    )


@blueprint.route('/api/universities', methods=['POST'])
def create_university():
    if not request.json:
        return make_response(jsonify({'error': 'Отсутствуют аргументы'}), 400)
    elif not all(key in request.json
                 for key in ['name', 'address', 'email', 'faculties', 'competitions']):
        return make_response(jsonify({'error': 'Bad request'}), 400)

    db_sess = create_session()
    university = Universities()
    university.name = request.json['name']
    university.address = request.json['address']
    university.email = request.json['email']
    university.faculties = request.json['faculties']
    university.competitions = request.json['competitions']
    db_sess.add(university)
    db_sess.commit()

    return make_response({'id': university.id, 'message': 'Университет был успешно создан'}, 200)


@blueprint.route('/api/universities/<int:university_id>', methods=['PUT'])
def edit_university(university_id: int):
    db_sess = create_session()
    university = db_sess.query(Universities).get(university_id)

    if not university:
        return make_response(jsonify({'error': 'Университет не был найден'}), 404)
    elif not request.json:
        return make_response(jsonify({'error': 'Пустой запрос'}), 400)
    elif not all(key in ['name', 'address', 'email', 'faculties', 'competitions']
                 for key in request.json):
        return make_response(jsonify({'error': 'Bad request'}), 400)

    for key in request.json:
        if key == 'name':
            university.name = request.json[key]
        elif key == 'address':
            university.address = request.json[key]
        elif key == 'email':
            university.email = request.json[key]
        elif key == 'faculties':
            university.faculties = request.json[key]
        elif key == 'competitions':
            university.competitions = request.json[key]

    db_sess.add(university)
    db_sess.commit()

    return make_response(jsonify({'message': 'Изменения прошли успешно'}), 200)


@blueprint.route('/api/universities/<int:university_id>', methods=['DELETE'])
def delete_university(university_id):
    db_sess = create_session()
    university = db_sess.query(Universities).get(university_id)

    if not university:
        return make_response(jsonify({'error': 'University not found'}, 404))

    db_sess.delete(university)
    db_sess.commit()

    return make_response(jsonify({'message': 'Университет был успешно удалён'}), 200)
