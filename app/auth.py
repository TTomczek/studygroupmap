import bcrypt
from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_user, logout_user, login_required

from .models import User
from . import db, app

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET'])
def login():
    return render_template('login.html', title='Login')


@auth.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    remember_me = True if request.form.get('remember') else False

    user = User.query.filter_by(username=username).first()

    if not user:
        return render_template('login.html', title='Login',
                               message='Benutzername oder Passwort falsch.')

    pepper = app.config['PEPPER']
    if not User.check_password(password, user.password):
        flash('Benutzername oder Passwort falsch.', 'danger')
        return render_template('login.html', title='Login')

    login_user(user, remember=remember_me)
    return redirect(url_for('main.dashboard'))


@auth.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html', title='Registrieren')


@auth.route('/signup', methods=['POST'])
def signup_post():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')

    user = User.query.filter_by(email=email).first()

    if user:
        flash('Diese E-Mail-Adresse wird bereits verwendet.', "warning")
        return render_template('signup.html', title='Registrieren')

    new_user = User(email=email, username=username, password=User.hash_password(password))

    db.session.add(new_user)
    db.session.commit()

    flash("Registrierung erfolgreich.", "success")
    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))



