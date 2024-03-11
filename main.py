import os
from flask import Flask, url_for, request, render_template, redirect, abort
import requests
import json
import random
import sqlite3
from data import db_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from requests import session
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField, IntegerField, DateField
from wtforms.validators import DataRequired, Email, NumberRange
from flask_wtf import FlaskForm
from flask_login import login_user, current_user, LoginManager, logout_user, login_required
from data.universities import Universities
from data.users import User

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

basedir = os.path.abspath(os.path.dirname(__file__))
db_session.global_init(os.path.join(basedir, 'db', 'universities.db'))
db_sess = db_session.create_session()


@login_manager.user_loader
def load_user(user_id: int):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def works_log():
    universities = db_sess.query(Universities).all()
    return render_template('universities.html', title='Журнал работ', universities=universities)


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль')
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form,
                               current_user=current_user)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


class RegistrationForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    repeat_password = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        user.surname = form.surname.data
        user.name = form.name.data
        user.email = form.email.data
        user.password = form.password.data
        user.address = form.address.data
        db_sess.add(user)
        db_sess.commit()

    return render_template('register.html', form=form)


if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = 'random_key'
    app.run(port=5000, host='127.0.0.1')
