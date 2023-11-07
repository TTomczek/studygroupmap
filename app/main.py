from flask import Blueprint, url_for, redirect, render_template, request, flash
from flask_login import login_required, current_user

from app import db
from app.models import User
from app.form.profile_form import ProfileForm

main = Blueprint('main', __name__)


@main.route('/')
def redirect_index():
    return redirect(url_for('main.dashboard'), code=302, Response=None)


@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.isFirstLogin:
        flash("Bitte vervollständige dein Profil.", "warning")
        return redirect(url_for('main.profile'))
    else:
        return render_template('dashboard.html', title='Dashboard')


@main.route('/profile')
@login_required
def profile():
    profile_form = ProfileForm(user=current_user)
    return render_template('profile.html', title='Profil bearbeiten', user=current_user, form=profile_form)


@main.route('/profile', methods=['POST'])
@login_required
def profile_post():

    form = ProfileForm(request.form)

    if not form.validate():
        return render_template('profile.html', title='Profil bearbeiten', user=current_user, form=form)

    user = User.query.filter_by(id=current_user.id).first()
    user.isFirstLogin = False
    user.username = form.username.data
    user.firstname = form.firstname.data
    user.lastname = form.lastname.data
    user.email = form.email.data
    user.phone = form.phone.data
    user.studentnumber = form.studentnumber.data
    user.courseofstudy = form.courseofstudy.data
    user.semester = form.semester.data
    user.street = form.street.data
    user.postcode = form.postcode.data
    user.city = form.city.data
    user.country = form.country.data

    if form.password.data:
        user.password = User.hash_password(form.password.data)

    db.session.commit()
    flash("Profil erfolgreich aktualisiert.", "success")
    return redirect(url_for('main.profile'))
