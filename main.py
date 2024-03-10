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

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init('db/universities.db')
db_sess = db_session.create_session()


@app.route('/')
def works_log():
    universities = db_sess.query(Universities).all()
    return render_template('universities.html', title='Журнал работ', jobs=universities)


if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = 'random_key'
    app.run(port=5000, host='127.0.0.1')
