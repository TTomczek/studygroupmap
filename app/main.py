from flask import Blueprint, url_for, redirect, render_template, request, flash
from flask_login import login_required, current_user
from folium import folium, Marker, Icon

from app import db
from app.database import User, get_studygroups_of_user_for_dashboard, Studygroup, StudygroupUser
from app.form.group_form import GroupForm
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

    dashboard_map = get_centered_map(current_user)

    return render_template('dashboard.html',
                           title='Dashboard',
                           studygroups=get_studygroups_of_user_for_dashboard(current_user),
                           map=dashboard_map.get_root()._repr_html_())


@main.route('/dashboard/students')
@login_required
def dashboard_students():

    users = User.query.all()
    student_map = get_centered_map(current_user)

    for user in users:

        color = "blue"
        if user.id == current_user.id:
            color = "green"

        if user.latitude != 0 and user.longitude != 0:
            (Marker([user.latitude, user.longitude],
                    popup=get_student_popup(user),
                    icon=Icon(icon="person", color=color, prefix="fa", icon_color="white"),
                    tooltip=user.firstname + " " + user.lastname + " (" + user.username + ")")
             .add_to(student_map))

    return student_map.get_root()._repr_html_()


@main.route('/dashboard/groups')
@login_required
def dashboard_groups():

    groups = Studygroup.query.all()
    group_map = get_centered_map(current_user)
    group_ids_of_current_user = [group.id for group in get_studygroups_of_user_for_dashboard(current_user)]

    for group in groups:

        color = "blue"
        if group.id in group_ids_of_current_user:
            color = "green"
        (Marker(group.get_group_location(),
               popup=group.name,
               icon=Icon(icon="people-group", color=color, prefix="fa", icon_color="white"))
         .add_to(group_map))

    return group_map.get_root()._repr_html_()


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


@main.route('/group/<int:group_id>')
@login_required
def edit_group(group_id: int, group_form=None):

    group = Studygroup.query.filter_by(id=group_id).first()
    member = group.get_member()

    if current_user.id not in [user.id for user in member]:
        flash("Du bist kein Mitglied dieser Gruppe.", "danger")
        return redirect(url_for('main.dashboard'))

    if group_form is None:
        group_form = GroupForm(group=group, current_user=current_user)


    return render_template('group.html', title='Gruppe bearbeiten', form=group_form,
                           member=member, current_user=current_user)


@main.route('/group/<int:group_id>', methods=['POST'])
@login_required
def edit_group_post(group_id: int):

    group_form = GroupForm(request.form, current_user=current_user)

    if not group_form.validate():
        print(group_form.id.data)
        return edit_group(group_id, group_form)

    group = Studygroup.query.filter_by(id=group_id).first()
    group.name = group_form.name.data.strip()
    group.description = group_form.description.data.strip()
    db.session.commit()

    flash("Gruppe erfolgreich aktualisiert.", "success")
    return redirect(url_for('main.edit_group', group_id=group_id))


@main.route('/group/<int:group_id>/member/<int:user_id>', methods=['POST'])
@login_required
def remove_group_member(group_id: int, user_id: int):

    user_group = StudygroupUser.query.filter_by(studygroup=group_id, user=user_id).first()

    if user_group is None:
        flash("Benutzer nicht gefunden.", "danger")
        return edit_group(group_id)

    StudygroupUser.query.filter_by(studygroup=group_id, user=user_id).delete()
    db.session.commit()

    if user_id == current_user.id:
        flash("Du hast die Gruppe erfolgreich verlassen.", "success")
        return redirect(url_for('main.dashboard'))

    flash("Benutzer erfolgreich entfernt.", "success")
    return edit_group(group_id)


def check_address_changed(user: User, form: ProfileForm):

    return (user.street != form.street.data.strip() or user.postcode != form.postcode.data.strip() or
            user.city != form.city.data.strip() or user.country != form.country.data.strip())


def get_centered_map(user, inital_zoom_level=10):

    if user.latitude == 0 or user.longitude == 0:
        return folium.Map(location=[51.5, 10], zoom_start=inital_zoom_level, scrollWheelZoom=False)
    else:
        return folium.Map(location=[user.latitude, user.longitude], zoom_start=inital_zoom_level, scrollWheelZoom=False)


def get_student_popup(user: User):
    return '''
    <div class="custom-leaflet-popup-content">
        <div>Name: {0} {1}</div>
        <div>Studiengang: {2}</div>
        <div>Semester: {3}</div>
        <div class="userPopupToolbar">
            <button class="btn btn-primary">Profil anzeigen</button>
            <button class="btn btn-primary">Zu Gruppe einladen</button>
        </div>
    </div>
    '''.format(user.firstname, user.lastname, user.courseofstudy, user.semester)
