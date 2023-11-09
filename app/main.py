from flask import Blueprint, url_for, redirect, render_template, request, flash
from flask_login import login_required, current_user
from folium import folium

from app import db
from app.database import User, get_studygroups_of_user_for_dashboard
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

    if current_user.latitude == 0 or current_user.longitude == 0:
        dashboard_map = folium.Map(location=[51.5, 10], zoom_start=10, scrollWheelZoom=False)
    else:
        dashboard_map = folium.Map(location=[current_user.latitude, current_user.longitude], zoom_start=10)

    return render_template('dashboard.html',
                           title='Dashboard',
                           studygroups=get_studygroups_of_user_for_dashboard(current_user),
                           map=dashboard_map.get_root()._repr_html_())


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

    if check_address_changed(user, form):
        user.update_location()

    user.isFirstLogin = False
    user.username = form.username.data.strip().strip()
    user.firstname = form.firstname.data.strip()
    user.lastname = form.lastname.data.strip()
    user.email = form.email.data.strip()
    user.phone = form.phone.data.strip()
    user.studentnumber = form.studentnumber.data.strip()
    user.courseofstudy = form.courseofstudy.data.strip()
    user.semester = form.semester.data
    user.street = form.street.data.strip()
    user.postcode = form.postcode.data.strip()
    user.city = form.city.data.strip()
    user.country = form.country.data.strip()

    if form.password.data:
        user.password = User.hash_password(form.password.data)

    db.session.commit()
    flash("Profil erfolgreich aktualisiert.", "success")
    return redirect(url_for('main.profile'))


def check_address_changed(user: User, form: ProfileForm):
    return user.street != form.street.data.strip() or user.postcode != form.postcode.data.strip() or user.city != form.city.data.strip() or user.country != form.country.data.strip()

