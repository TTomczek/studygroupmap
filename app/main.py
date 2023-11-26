from branca.element import CssLink
from flask import Blueprint, url_for, redirect, render_template, request, flash
from flask_login import login_required, current_user
from folium import folium, Marker, Icon
from sqlalchemy import and_

from app import db
from app.database import User, StudyGroup, StudygroupUser, JoinRequest, get_join_requests_for_group, \
    get_invitations_for_user
from app.form.groupform import GroupForm
from app.form.groupinviteform import AddToGroupForm
from app.form.groupjoinrequest import GroupJoinRequest
from app.form.profileform import ProfileForm

main = Blueprint('main', __name__)


@main.route('/')
def redirect_index():
    """Umleitung auf die Startseite."""
    return redirect(url_for('main.dashboard'), code=302, Response=None)


@main.route('/dashboard')
@login_required
def dashboard():
    """Anzeigen des Dashboards."""
    if current_user.isFirstLogin:
        flash("Bitte vervollständige dein Profil.", "warning")
        return redirect(url_for('main.profile'))

    return render_template('dashboard.html',
                           title='Dashboard',
                           current_user=current_user,
                           studygroups=User.get_studygroups_of_user_for_dashboard(current_user),
                           join_requests=get_invitations_for_user(current_user.id))


@main.route('/dashboard/map/students')
@login_required
def dashboard_students():
    """Zeige Karte der Nutzer."""
    other_users = User.query.filter(and_(User.can_be_invited, User.id != current_user.id)).all()

    search_string = request.args.get('search_string', default="", type=str)
    if search_string != "":
        filtered_users = __filter_users_by_search_string(other_users, search_string)
    else:
        filtered_users = other_users

    filtered_users.append(current_user)

    student_map = __get_centered_map(current_user, height="50%")

    for user in filtered_users:

        color = "blue"
        if user.id == current_user.id:
            color = "green"

        if user.latitude != 0 and user.longitude != 0:
            (Marker([user.latitude, user.longitude],
                    popup=__get_student_popup(user),
                    icon=Icon(icon="person", color=color, prefix="fa", icon_color="white"),
                    tooltip=user.firstname + " " + user.lastname)
             .add_to(student_map))

    return student_map.get_root()._repr_html_()


def __filter_users_by_search_string(users, search_string):
    """Filtern der Nutzer nach Suchbegriff."""
    search_keywords = search_string.split(" ")
    return [user for user in users if
            any(keyword.lower() in user.firstname.lower()
                or keyword.lower() in user.lastname.lower()
                or keyword.lower() in user.courseofstudy.lower()
                or keyword.lower() in user.about_me.lower()
                or __check_semester(keyword, user)
                for keyword in search_keywords)]


def __check_semester(keyword: str, user: User):
    try:
        return int(keyword) == user.semester
    except ValueError:
        return False


@main.route('/dashboard/map/groups')
@login_required
def dashboard_groups():
    """Zeige Karte der Gruppen."""
    group_ids_of_cu = [group.id for group in User.get_studygroups_of_user_for_dashboard(current_user)]
    my_groups = StudyGroup.query.filter(StudyGroup.id.in_(group_ids_of_cu)).all()

    other_open_groups = StudyGroup.query.filter(
        and_(
            StudyGroup.is_open == True,
            StudyGroup.id.not_in(group_ids_of_cu)
        )
    ).all()

    search_string = request.args.get('search_string', default="", type=str)
    if search_string != "":
        filtered_other_open_groups = __filter_groups_by_search_string(other_open_groups, search_string)
    else:
        filtered_other_open_groups = other_open_groups

    groups = my_groups + filtered_other_open_groups
    group_map = __get_centered_map(current_user, height="50%")

    for group in groups:
        color = "blue"
        if group.id in group_ids_of_cu:
            color = "green"
        (Marker(group.get_group_location(),
                popup=__get_group_popup(group),
                icon=Icon(icon="people-group", color=color, prefix="fa", icon_color="white"))
         .add_to(group_map))

    return group_map.get_root()._repr_html_()


def __filter_groups_by_search_string(groups, search_string):
    """Filtern der Gruppen nach Suchbegriff."""
    search_keywords = search_string.split(" ")
    return [group for group in groups if
            any(keyword.lower() in group.name.lower() or keyword.lower() in group.description.lower()
                for keyword in search_keywords)]


@main.route('/profile')
@login_required
def profile():
    """Anzeigen des Profils."""
    profile_form = ProfileForm(user=current_user)
    return render_template('profile.html', title='Profil bearbeiten', user=current_user, form=profile_form)


@main.route('/profile', methods=['POST'])
@login_required
def profile_post():
    """Aktualisieren des Profils."""
    form = ProfileForm(request.form)

    if not form.validate():
        return render_template('profile.html', title='Profil bearbeiten', user=current_user, form=form)

    user = User.query.filter_by(id=current_user.id).first()

    if __check_address_changed(user, form):
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
    user.can_be_invited = form.can_be_invited.data
    user.about_me = form.about_me.data.strip()
    user.latitude = form.latitude.data.strip()
    user.longitude = form.longitude.data.strip()

    if form.password.data:
        user.password = User.hash_password(form.password.data)

    db.session.commit()
    flash("Profil erfolgreich aktualisiert.", "success")
    return redirect(url_for('main.profile'))


@main.route('/profile/map')
@login_required
def profile_map():
    """Zeige Karte des Standortes des Nutzers."""
    user = current_user
    profile_map = __get_centered_map(user, inital_zoom_level=15, height="40%")

    if user.latitude != 0 and user.longitude != 0:
        (Marker([user.latitude, user.longitude],
                popup=__get_student_popup(user),
                icon=Icon(icon="person", color="green", prefix="fa", icon_color="white"),
                tooltip=user.firstname + " " + user.lastname)
         .add_to(profile_map))

    return profile_map.get_root()._repr_html_()


@main.route('/group/<int:group_id>')
@login_required
def edit_group(group_id: int, group_form=None):
    """Anzeigen und Bearbeiten der Gruppe."""
    group = StudyGroup.query.filter_by(id=group_id).first()
    member = group.get_member()

    if current_user.id not in [user.id for user in member]:
        flash("Du bist kein Mitglied dieser Gruppe.", "danger")
        return redirect(url_for('main.dashboard'))

    owner_options = [(user.id, user.firstname + " " + user.lastname) for user in member]

    if group_form is None:
        group_form = GroupForm(group=group, current_user=current_user, owner_options=owner_options)

    return render_template('group.html', title='Gruppe bearbeiten', form=group_form, member=member,
                           current_user=current_user, join_requests=get_join_requests_for_group(group_id),
                           submit_endpoint=url_for('main.edit_group_post', group_id=group_id))


@main.route('/group/<int:group_id>', methods=['POST'])
@login_required
def edit_group_post(group_id: int):
    """Aktualisieren der Gruppe."""
    group = StudyGroup.query.filter_by(id=group_id).first()
    member = group.get_member()
    owner_options = [(user.id, user.firstname + " " + user.lastname) for user in member]
    group_form = GroupForm(request.form, current_user=current_user, owner_options=owner_options)

    if not group_form.validate():
        return edit_group(group_id, group_form)

    group = StudyGroup.query.filter_by(id=group_id).first()
    group.name = group_form.name.data.strip()
    group.description = group_form.description.data.strip()
    group.is_open = group_form.is_open.data
    group.owner = group_form.owner.data
    db.session.commit()

    flash("Gruppe erfolgreich aktualisiert.", "success")
    return redirect(url_for('main.edit_group', group_id=group_id,
                            submit_endpoint=url_for('main.edit_group_post', group_id=group_id)))


@main.route('/group/<int:group_id>/member/<int:user_id>', methods=['POST'])
@login_required
def remove_group_member(group_id: int, user_id: int):
    """Entfernen eines Mitglieds aus der Gruppe."""
    user_group_to_remove = StudygroupUser.query.filter_by(studygroup=group_id, user=user_id).first()

    if user_group_to_remove is None:
        flash("Benutzer nicht gefunden.", "danger")
        return edit_group(group_id)

    group = StudyGroup.query.filter_by(id=group_id).first()
    if user_id == group.owner:
        new_owner = StudygroupUser.query.filter_by(studygroup=group_id).filter(StudygroupUser.user != user_id).first()

        if new_owner is None:
            flash("Die Gruppe wurde aufgelöst.", "success")
            db.session.delete(group)
        else:
            group.owner = new_owner.invited_user

    db.session.delete(user_group_to_remove)

    if user_id == current_user.id:
        flash("Du hast die Gruppe erfolgreich verlassen.", "success")
        return redirect(url_for('main.dashboard'))

    flash("Benutzer erfolgreich entfernt.", "success")
    return edit_group(group_id)


@main.route('/group/create')
@login_required
def create_group():
    """Anzeigen des Formulares zur Erstellung einer neuen Gruppe."""
    group = StudyGroup(name="Neue Gruppe")
    group.is_open = True
    group.owner = current_user.id

    owner_options = [(current_user.id, current_user.firstname + " " + current_user.lastname)]
    form = GroupForm(current_user=current_user, group=group, owner_options=owner_options)
    return render_template('group.html', title='Gruppe erstellen', form=form,
                           submit_endpoint=url_for('main.create_group_post'))


@main.route('/group/create', methods=['POST'])
@login_required
def create_group_post():
    """Erstellen einer neuen Gruppe."""
    owner_options = [(current_user.id, current_user.firstname + " " + current_user.lastname)]
    form = GroupForm(request.form, current_user=current_user, owner_options=owner_options)

    if not form.validate():
        return render_template('group.html', title='Gruppe erstellen', form=form)

    group = StudyGroup(name=form.name.data.strip(), description=form.description.data.strip(), owner=form.owner.data)
    group.is_open = form.is_open.data
    db.session.add(group)
    db.session.commit()

    studygroup_user = StudygroupUser(studygroup=group.id, user=current_user.id)
    db.session.add(studygroup_user)
    db.session.commit()

    flash("Gruppe erfolgreich erstellt.", "success")
    return redirect(url_for('main.edit_group', group_id=group.id))


@main.route('/group/join/<int:invited_user_id>', methods=['GET'])
@login_required
def join(invited_user_id: int):
    """Anzeigen des Formulares zum Einladen eines Nutzers in eine Gruppe."""
    groups_of_current_user = StudygroupUser.get_groups_ids_of_user(current_user.id)
    groups_of_invited_user = StudygroupUser.get_groups_ids_of_user(invited_user_id)
    possible_group_ids = [x.id for x in groups_of_current_user if x not in groups_of_invited_user]
    possible_groups = StudyGroup.query.filter(StudyGroup.id.in_(possible_group_ids)).all()
    group_choices = [(group.id, group.name) for group in possible_groups]

    invited_user = User.query.filter_by(id=invited_user_id).first()
    invited_user_name = invited_user.firstname + " " + invited_user.lastname

    form = AddToGroupForm(group_choices=group_choices)
    form.invited_user.data = invited_user_id
    return render_template('groupinvitation.html', title="Nutzer zu Gruppe einladen", form=form,
                           group_choices=group_choices, invited_user_name=invited_user_name)


@main.route('/group/join', methods=['POST'])
@login_required
def join_post():
    """Einladen eines Nutzers in eine Gruppe."""
    form = AddToGroupForm(request.form, group_choices=[])

    if JoinRequest.query.filter_by(studygroup=form.group.data, invited_user=form.invited_user.data,
                                   accepted=None).first() is not None:
        flash("Der Benutzer wurde bereits zu dieser Gruppe eingeladen.", "danger")
        return redirect(url_for('main.dashboard'))

    join_request = JoinRequest(studygroup_id=form.group.data, invited_user_id=form.invited_user.data,
                               invited_by_id=current_user.id, message=form.message.data.strip())
    flash("Einladung erfolgreich versendet.", "success")
    db.session.add(join_request)
    db.session.commit()

    return redirect(url_for('main.edit_group', group_id=form.group.data))


@main.route('/group/join/<int:join_request_id>/<int:accepted>')
@login_required
def answer_group_join_request(join_request_id: int, accepted: int):
    """Beantworten einer Beitrittsanfrage."""
    join_request = JoinRequest.query.filter_by(id=join_request_id).first()

    if join_request is None:
        flash("Einladung nicht gefunden.", "danger")
        return redirect(url_for('main.dashboard'))

    group = StudyGroup.query.filter_by(id=join_request.studygroup).first()

    if group is None:
        flash("Gruppe nicht gefunden.", "danger")
        db.session.delete(join_request)
        db.session.commit()
        return redirect(url_for('main.dashboard'))

    is_invitation = join_request.invited_by is not None

    if is_invitation:

        if join_request.invited_user != current_user.id:
            flash("Du bist nicht berechtigt diese Anfrage zu beantworten.", "danger")
            return redirect(url_for('main.dashboard'))
    else:

        if group.owner != current_user.id:
            flash("Du bist nicht berechtigt diese Anfrage zu beantworten.", "danger")
            return redirect(url_for('main.dashboard'))

    if accepted == 1:
        return __accept_join_request(join_request, group, is_invitation)
    else:
        return __decline_join_request(join_request, is_invitation)


@main.route('/group/join/request/<int:group_id>')
@login_required
def group_join_request(group_id: int):
    """Anzeigen des Formulares zum Anfragen eines Beitritts zu einer Gruppe."""
    group = StudyGroup.query.filter_by(id=group_id).first()

    if group is None:
        flash("Gruppe nicht gefunden.", "danger")
        return redirect(url_for('main.dashboard'))

    if StudygroupUser.query.filter_by(studygroup=group_id, user=current_user.id).first() is not None:
        flash("Du bist bereits in der Gruppe.", "danger")
        return redirect(url_for('main.dashboard'))

    if not group.is_open:
        flash("Du kannst der Gruppe momentan nicht beitreten.", "danger")
        return redirect(url_for('main.dashboard'))

    if JoinRequest.query.filter_by(studygroup=group_id, invited_user=current_user.id,
                                   accepted=None).first() is not None:
        flash("Du hast einen Beitritt zu dieser Gruppe bereits angefragt oder wurdest zu ihr bereits eingeladen.",
              "danger")
        return redirect(url_for('main.dashboard'))

    form = GroupJoinRequest(group_id=group.id)

    return render_template('groupjoinrequest.html', form=form, group=group, title="Gruppenbeitritt anfragen")


@main.route('/group/join/request/<int:group_id>', methods=['POST'])
@login_required
def group_join_request_post(group_id: int):
    """Anfragen eines Beitritts zu einer Gruppe."""
    form = GroupJoinRequest(request.form, group_id=group_id)

    if JoinRequest.query.filter_by(studygroup=group_id, invited_user=current_user.id,
                                   accepted=None).first() is not None:
        flash("Du hast einen Beitritt zu dieser Gruppe bereits angefragt oder wurdest zu ihr bereits eingeladen.",
              "danger")
        return redirect(url_for('main.dashboard'))

    join_request = JoinRequest(studygroup_id=group_id, invited_user_id=current_user.id,
                               invited_by_id=None, message=form.message.data.strip())
    db.session.add(join_request)
    db.session.commit()

    flash("Beitrittsanfrage erfolgreich versendet.", "success")
    return redirect(url_for('main.dashboard'))


def __accept_join_request(join_request: JoinRequest, group: StudyGroup, is_invitation: bool):
    """Akzeptieren einer Beitrittsanfrage."""
    if StudygroupUser.query.filter_by(studygroup=join_request.studygroup,
                                      user=join_request.invited_user).first() is not None:

        if is_invitation:
            flash("Du bist bereits in der Gruppe.", "danger")
        else:
            flash("Der Benutzer ist bereits in der Gruppe.", "danger")

        join_request.accepted = True
        db.session.commit()
        return redirect(url_for('main.dashboard'))

    join_request.accepted = True

    studygroup_user = StudygroupUser(studygroup=join_request.studygroup, user=join_request.invited_user)
    db.session.add(studygroup_user)
    db.session.commit()

    if is_invitation:
        flash("Du bist der Gruppe erfolgreich beigetreten.", "success")
    else:
        flash("Der Benutzer wurde erfolgreich zur Gruppe hinzugefügt.", "success")

    return redirect(url_for('main.edit_group', group_id=group.id))


def __decline_join_request(join_request: JoinRequest, is_invitation: bool):
    """Ablehnen einer Beitrittsanfrage."""
    join_request.accepted = False
    db.session.commit()

    if is_invitation:

        flash("Du hast die Einladung abgelehnt.", "success")
    else:

        flash("Die Anfrage wurde abgelehnt.", "success")
    return redirect(url_for('main.dashboard'))


def __check_address_changed(user: User, form: ProfileForm):
    """Prüfen ob sich die Adresse geändert hat."""
    return (user.street != form.street.data.strip() or user.postcode != form.postcode.data.strip() or
            user.city != form.city.data.strip() or user.country != form.country.data.strip())


def __get_centered_map(user, inital_zoom_level=10, width="100%", height="100%"):
    """Erstellen einer Karte mit dem Standort des Nutzers in der Mitte."""
    if user.latitude == 0 or user.longitude == 0:
        flash("Der Standort konnte nicht ermittelt werden.", "warning")
        folium_map = folium.Map(location=[51.5, 10], zoom_start=inital_zoom_level, scrollWheelZoom=False,
                                width=width, height=height)
    else:
        folium_map = folium.Map(location=[user.latitude, user.longitude], zoom_start=inital_zoom_level,
                                scrollWheelZoom=False, width=width, height=height)

    folium_map.get_root().header.add_child(CssLink(url_for('static', filename='css/style.css')))
    return folium_map


def __get_student_popup(user: User):
    """Erstellen eines Popups für einen Nutzer."""
    return render_template('studentmarkerpopup.html', user=user)


def __get_group_popup(group: StudyGroup):
    """Erstellen eines Popups für eine Gruppe."""
    group_owner_user = group.get_owner_user()
    group_owner_name = group_owner_user.firstname + " " + group_owner_user.lastname

    return render_template('groupmarkerpopup.html', group=group, group_owner_name=group_owner_name)
