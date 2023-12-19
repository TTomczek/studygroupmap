from .database import User, StudyGroup, StudygroupUser, JoinRequest


def init_db(db):
    if User.query.filter_by(username="user1").first() is None:
        user1 = User(username="user1", email="user1@user1.mail", password=User.hash_password("user1"))
        user1.firstname = "Achim"
        user1.lastname = "Metzler"
        user1.city = "Bochum"
        user1.country = "Deutschland"
        user1.street = "Heuweg 5"
        user1.postcode = "44805"
        user1.phone = "+49 30 314-0"
        user1.studentnumber = "111111111"
        user1.courseofstudy = "Computer Science"
        user1.semester = "3"
        user1.isFirstLogin = False
        user1.latitude = 51.5151783
        user1.longitude = 7.2816362
        user1.about_me = '''
            Hallo! Ich bin Achim, ein Student im dritter Semester. 🎓
            In meiner Freizeit liebe ich es, mich mit Tieren und Programmierung zu beschäftigen. Als Informatikstudent habe ich bereits einige spannende Projekte umgesetzt, darunter eine Webanwendung zur Verwaltung von Aufgaben und eine App zur Erkennung von Pflanzenarten.
            Meine Leidenschaft für das Lernen und die Neugierde auf neue Herausforderungen treiben mich an. Ich bin stets bestrebt, mein Wissen zu erweitern und mich persönlich weiterzuentwickeln.
            Neben dem Studium engagiere ich mich in der Hochschulgruppe für künstliche Intelligenz und bin Teil des Organisationsteams für Hackathons. Hier kann ich meine Fähigkeiten in der Teamarbeit und im Projektmanagement unter Beweis stellen.
        '''
        db.session.add(user1)

    if User.query.filter_by(username="user2").first() is None:
        user2 = User(username="user2", email="user2@user2.mail", password=User.hash_password("user2"))
        user2.firstname = "Christoper"
        user2.lastname = "Schneider"
        user2.city = "Lünen"
        user2.country = "Deutschland"
        user2.street = "Rathenaustraße 35"
        user2.postcode = "44534"
        user2.phone = "+49 30 462-1"
        user2.studentnumber = "222222222"
        user2.courseofstudy = "Computer Science"
        user2.semester = "3"
        user2.isFirstLogin = False
        user2.latitude = 51.6093647
        user2.longitude = 7.5123653
        user2.can_be_invited = False
        db.session.add(user2)

    if User.query.filter_by(username="user3").first() is None:
        user3 = User(username="user3", email="user3@user3.mail", password=User.hash_password("user3"))
        user3.firstname = "Cem"
        user3.lastname = "Ibrahim"
        user3.city = "Holzwickede"
        user3.country = "Deutschland"
        user3.street = "Hamburger Allee 11"
        user3.postcode = "59439"
        user3.phone = "+49 30 752-4"
        user3.studentnumber = "333333333"
        user3.courseofstudy = "Computer Science"
        user3.semester = "3"
        user3.isFirstLogin = False
        user3.latitude = 51.5001804
        user3.longitude = 7.6162948
        user3.about_me = '''
            Hallo! Ich bin Max, ein aufgeschlossener Student im zweiten Semester. 🎓
            In meiner Freizeit liebe ich es, mich mit Technologie und Programmierung zu beschäftigen. Als Informatikstudent habe ich bereits einige spannende Projekte umgesetzt, darunter eine Webanwendung zur Verwaltung von Aufgaben und eine App zur Erkennung von Pflanzenarten.
            Meine Leidenschaft für das Lernen und die Neugierde auf neue Herausforderungen treiben mich an. Ich bin stets bestrebt, mein Wissen zu erweitern und mich persönlich weiterzuentwickeln.
            Neben dem Studium engagiere ich mich in der Hochschulgruppe für künstliche Intelligenz und bin Teil des Organisationsteams für Hackathons. Hier kann ich meine Fähigkeiten in der Teamarbeit und im Projektmanagement unter Beweis stellen.
            In meiner Zukunft sehe ich mich als Softwareentwickler, der innovative Lösungen für reale Probleme entwickelt. Obwohl ich noch viel zu lernen habe, bin ich zuversichtlich, dass ich meinen Weg gehen werde.
            Wenn du Fragen hast oder dich für meine Projekte interessierst, zögere nicht, mich anzusprechen! Ich freue mich darauf, dich kennenzulernen. 😊
        '''
        db.session.add(user3)

    if User.query.filter_by(username="user4").first() is None:
        user4 = User(username="user4", email="user4@user4.mail", password=User.hash_password("user4"))
        user4.firstname = "Jakob"
        user4.lastname = "Müller"
        user4.city = "Hagen"
        user4.country = "Deutschland"
        user4.street = "Siegstraße 21"
        user4.postcode = "58097"
        user4.phone = "+49 30 563-7"
        user4.studentnumber = "444444444"
        user4.courseofstudy = "Computer Science AI"
        user4.semester = "7"
        user4.isFirstLogin = False
        user4.latitude = 51.3703058
        user4.longitude = 7.4655616
        db.session.add(user4)

    if User.query.filter_by(username="user5").first() is None:
        user5 = User(username="user5", email="user5@user5.mail", password=User.hash_password("user5"))
        user5.firstname = "Peter"
        user5.lastname = "Mayer"
        user5.city = "Schwerte"
        user5.country = "Deutschland"
        user5.street = "Letmather Str. 131"
        user5.postcode = "58239"
        user5.phone = "+49 30 975-1"
        user5.studentnumber = "555555555"
        user5.courseofstudy = "Computer Science AI"
        user5.semester = "7"
        user5.isFirstLogin = False
        user5.latitude = 51.4180251
        user5.longitude = 7.567113
        db.session.add(user5)

    if User.query.filter_by(username="user6").first() is None:
        user6 = User(username="user6", email="user6@user6.mail", password=User.hash_password("user6"))
        user6.firstname = ""
        user6.lastname = ""
        user6.city = ""
        user6.country = ""
        user6.street = ""
        user6.postcode = ""
        user6.phone = ""
        user6.studentnumber = ""
        user6.courseofstudy = ""
        user6.semester = ""
        user6.isFirstLogin = True
        db.session.add(user6)

    db.session.commit()

    if StudyGroup.query.filter_by(name="AI Gruppe").first() is None:
        group1 = StudyGroup(name="AI Gruppe", description="Gruppe zur Erforschung der Vernichtung der Menschheit")
        group1.owner = 4
        db.session.add(group1)

    if StudyGroup.query.filter_by(name="Computer Gruppe").first() is None:
        group2 = StudyGroup(name="Computer Gruppe", description="Hallo, wir sind eine Gruppe von Computern, "
                                                                "die sich selbst als “Die Rechenkünstler” bezeichnen. "
                                                                "Wir sind stolz darauf, dass wir in der Lage sind,"
                                                                " komplexe Berechnungen in kürzester Zeit durchzuführen. "
                                                                "Wir sind auch sehr vielseitig und können in vielen verschiedenen "
                                                                "Bereichen eingesetzt werden, von der Wissenschaft bis zur Kunst. "
                                                                "Wir haben eine Menge Erfahrung und sind immer bereit, "
                                                                "neue Herausforderungen anzunehmen. Wir sind sehr "
                                                                "effizient und arbeiten hart, um sicherzustellen, "
                                                                "dass wir unsere Aufgaben schnell und genau erledigen. "
                                                                "Wir sind auch sehr freundlich und lieben es, mit anderen "
                                                                "Computern und Menschen zusammenzuarbeiten. Wir freuen uns"
                                                                " darauf, mit Ihnen zusammenzuarbeiten und Ihnen zu helfen,"
                                                                " Ihre Ziele zu erreichen.")
        group2.owner = 2
        group2.is_open = False
        db.session.add(group2)

    db.session.commit()

    StudygroupUser.query.delete()
    # AI Gruppe
    group41 = StudygroupUser(user=4, studygroup=1)
    group51 = StudygroupUser(user=5, studygroup=1)
    db.session.add(group41)
    db.session.add(group51)

    # Computer Gruppe
    group12 = StudygroupUser(user=1, studygroup=2)
    group22 = StudygroupUser(user=2, studygroup=2)
    group32 = StudygroupUser(user=3, studygroup=2)
    group42 = StudygroupUser(user=4, studygroup=2)
    db.session.add(group12)
    db.session.add(group22)
    db.session.add(group32)
    db.session.add(group42)

    db.session.commit()

    if JoinRequest.query.filter_by(invited_user=6, studygroup=1).first() is None:
        join_request = JoinRequest(invited_user_id=6, studygroup_id=1, invited_by_id=5, message="Du sollst auch AI studieren!")
        db.session.add(join_request)

    if JoinRequest.query.filter_by(invited_user=1, studygroup=1).first() is None:
        join_request = JoinRequest(invited_user_id=1, studygroup_id=1, message="LET ME IN!")
        db.session.add(join_request)

    db.session.commit()


