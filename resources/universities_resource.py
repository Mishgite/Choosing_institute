from flask_restful import reqparse, abort, Resource
from flask import jsonify

from data.db_session import create_session
from data.universities import Universities


parser = reqparse.RequestParser()
parser.add_argument('name', type=str, required=True)
parser.add_argument('email', type=str, required=True)
parser.add_argument('address', type=str, required=True)
parser.add_argument('faculties', type=list, required=True)
parser.add_argument('competitions', type=list, required=True)


def abort_if_university_doesnt_exist(university_id):
    db_sess = create_session()
    university = db_sess.query(Universities).get(university_id)

    if not university:
        abort(404, message=f'Университет с ID = {university_id} не найден')

    return university, db_sess


class UniversitiesResource(Resource):
    def get(self, university_id):
        university, _ = abort_if_university_doesnt_exist(university_id)
        return jsonify({'university': university.to_dict()})

    def delete(self, university_id):
        university, db_sess = abort_if_university_doesnt_exist(university_id)
        db_sess.delete(university)
        db_sess.commit()
        return jsonify({'message': 'Университет был удалён'})


class UniversitiesListResource(Resource):
    def get(self):
        db_sess = create_session()
        universities = db_sess.query(Universities).all()
        return jsonify({
            'universities': [university.to_dict()
                      for university in universities]
        })

    def post(self):
        args = parser.parse_args()
        db_sess = create_session()
        university = Universities()
        university.name = args['name']
        university.email = args['email']
        university.address = args['address']
        university.faculties = args['faculties']
        university.competitions = args['competitions']
        db_sess.add(university)
        db_sess.commit()

        return jsonify({'message': 'Университет был создан', 'id': university.id})
