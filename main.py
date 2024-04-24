import os
from flask import Flask, url_for, request, render_template, redirect, abort
import requests
import json
import sqlite3
import random
from data import db_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from requests import session
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField, IntegerField, DateField
from wtforms.validators import DataRequired, Email, NumberRange
from flask_wtf import FlaskForm
from flask_login import login_user, current_user, LoginManager, logout_user, login_required
from flask_restful import Api, abort
from data import __all_models
from data.universities import Universities
from data.users import User
from data.faculties_classes import Faculties_classes
from data.faculties import Faculties
from data.classes import Classes
from data.type import Type
import hashlib
import git

sha256_hash = hashlib.new('sha256')

app = Flask(__name__)
api = Api(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

basedir = os.path.abspath(os.path.dirname(__file__))
db_session.global_init(os.path.join(basedir, 'db', 'universities.db'))
db_sess = db_session.create_session()

id_usr = 1


@login_manager.user_loader
def load_user(user_id: int):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
@app.route('/home')
def works_log():
    universities = db_sess.query(Universities).all()
    return render_template('mainwindow.html', title='Университеты', universities=universities)


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль')
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/login', methods=['GET', 'POST'])
def login():
    global id_usr
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            id_usr = user.id
            return redirect('/')
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form,
                               current_user=current_user)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/about')
def about():
    return render_template('about.html')


class ScoresForm(FlaskForm):
    user = db_sess.query(User).filter(User.id == id_usr).first()
    score = IntegerField('Ваш балл', validators=[NumberRange(min=0, max=400)], default=user.min_ege_score)
    submit = SubmitField('Подобрать')


@app.route('/select_universities', methods=['GET', 'POST'])
def index():
    form = ScoresForm()
    if form.validate_on_submit():
        results = db_sess.query(Universities, Faculties).filter(Universities.id == Faculties.university_id
                                                                ).filter(Faculties.score <= form.score.data).all()
        return render_template('results.html', title='Результат', results=results)
    return render_template('select_universities.html', title='Подбор университета', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    repeat_password = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    min_ege_score = StringField('Баллы ЕГЭ', validators=[DataRequired()])
    submit = SubmitField('Создать Аккаунт')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        user.surname = form.surname.data
        user.name = form.name.data
        user.email = form.email.data
        user.hashed_password = form.password.data
        user.address = form.address.data
        user.min_ege_score = form.min_ege_score.data
        db_sess.add(user)
        db_sess.commit()
        print(user.surname)
        return redirect("/")

    return render_template('register.html', form=form)


@app.route('/faculties/<int:id>')
def faculties(id):
    universities = db_sess.query(Faculties).filter(Faculties.university_id == id)
    return render_template('faculties.html', title='Журнал факультетов', universities=universities)


@app.route('/user_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def user_delete(id: int):
    db_sess = db_session.create_session()
    if current_user.id == 1:
        user = db_sess.query(User).filter(User.id == id).first()
    else:
        user = db_sess.query(User).filter(User.id == id,).first()
    if user:
        db_sess.delete(user)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


class UserForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    min_ege_score = StringField('Баллы ЕГЭ', validators=[DataRequired()])
    submit = SubmitField('Готово')


@app.route('/user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_job(id: int):
    form = UserForm()
    if request.method == 'GET':
        db_sess = db_session.create_session()
        if current_user.id == 1:
            user = db_sess.query(User).filter(User.id == id).first()
        else:
            user = db_sess.query(User).filter(User.id == id).first()
        if user:
            form.email.data = user.email
            form.surname.data = user.surname
            form.name.data = user.name
            form.address.data = user.address
            form.min_ege_score.data = user.min_ege_score
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if current_user.id == 1:
            user = db_sess.query(User).filter(User.id == id).first()
        else:
            user = db_sess.query(User).filter(User.id == id).first()
        if user:
            user.email = form.email.data
            user.hashed_password = form.password.data
            user.surname = form.surname.data
            user.name = form.name.data
            form.address.data = user.address
            user.min_ege_score = form.min_ege_score.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('user_change.html', title='Изменить работу', form=form)


@app.route('/universities_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def universities_delete(id: int):
    db_sess = db_session.create_session()
    universities = db_sess.query(Universities).filter(Universities.id == id).first()
    if universities:
        db_sess.delete(universities)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/faculties_classes/<int:id>', methods=['GET', 'POST'])
def faculties_classes(id):
    classes = db_sess.query(Classes).filter(Faculties_classes.faculty_id == id,
                                            Faculties_classes.class_id == Classes.id)
    return render_template('classes.html', title='Журнал факультетов', classe=classes)


@app.route('/users_list', methods=['GET', 'POST'])
@login_required
def users_list():
    users = db_sess.query(User).all()
    type = db_sess.query(Type).all()
    return render_template('users.html', title='Журнал факультетов', users=users, type=type)


class SendingForm(FlaskForm):
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    patronymic = StringField('Отчество', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired(), Email()])
    address = StringField('Адрес', validators=[DataRequired()])
    min_ege_score = IntegerField('Баллы ЕГЭ', validators=[DataRequired()])
    want = StringField('Почему вы хотите на данный факультет', validators=[DataRequired()])
    submit = SubmitField('Готово')


@app.route('/sending/<int:id>', methods=['GET', 'POST'])
@login_required
def sending(id):
    faculties = db_sess.query(Faculties).filter(Faculties.university_id == id)
    return render_template('sending.html', title='Журнал факультетов', faculties=faculties)


class UniversityForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired(), Email()])
    address = StringField('Адрес', validators=[DataRequired()])
    submit = SubmitField('Готово')


@app.route('/add_university', methods=['GET', 'POST'])
@login_required
def add_university():
    form = UniversityForm()
    if form.validate_on_submit():
        university = Universities(name=form.name.data, email=form.email.data, address=form.address.data)
        db_sess.add(university)
        db_sess.commit()
        return redirect(f'/universities/{university.id}')
    return render_template('add_university.html', title='Добавить университет', form=form)


@app.route('/universities/<int:id>', methods=['GET', 'POST'])
@login_required
def view_university(id):
    university = db_sess.query(Universities).filter_by(id = id).first()
    return render_template('view_university.html', title='Университет', university=university)


@app.route('/edit_university/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_university(id):
    university = db_sess.query(Universities).filter_by(id=id).first()
    form = UniversityForm(name=university.name, email=university.email, address=university.address)
    if form.validate_on_submit():
        university.name = form.name.data
        university.email = form.email.data
        university.address = form.address.data
        db_sess.add(university)
        db_sess.commit()
        return redirect(f'/universities/{university.id}')
    return render_template('edit_university.html', title='Редактировать университет', form=form)

@app.route('/update_server', methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('Choosing_institute')
        origin = repo.remotes.origin
        origin.pull()
        return "Updated PythonAnywhere successfully", 200
    else:
        return "Wrong event type", 400


app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'random_key'


if __name__ == '__main__':
    from api import api_users, api_universities
    from resources import users_resource, universities_resource



    api.add_resource(users_resource.UsersResource, '/api/v2/users/<int:user_id>')
    api.add_resource(users_resource.UsersListResource, '/api/v2/users')
    api.add_resource(universities_resource.UniversitiesResource, '/api/v2/universities/<int:university_id>')
    api.add_resource(universities_resource.UniversitiesListResource, '/api/v2/universities')

    app.register_blueprint(api_users.blueprint)
    app.register_blueprint(api_universities.blueprint)

    app.run(port=5000, host='127.0.0.1')
