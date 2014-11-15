import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models import (
    DBSession,
    User,
    Base,
    Group,
    Question_Group,
    Question,
    Course,
    Exam,
    Answer,

    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        users = DBSession.query(User).all()
        if not users:
        # user1 = User(login_name='root', password='qdbwfnegm', first_name='Super User', last_name = 'Super User', email = 's.h.mahdavi@chmail.ir',
            user1 = User(login_name='root', password='1', first_name=' ', last_name = ' کاربر ارشد', email = 's.h.mahdavi@chmail.ir',
                     phone = '09106853582', mobile = '09106853582')
            user1.account = 200000000
            group1 = Group("group:admins")
            user1.groups.append(group1)
        # question_groups = DBSession.query(Question_Group).all()
        # if not question_groups:
            question_group1 = Question_Group(title='گروه اول')
            question_group2 = Question_Group(title='گروه دوم')

        # questions = DBSession.query(Question).all()
        # if not questions:
            question1 = Question(title='پایتخت ایران کجا است', time=30, comment=' ', correct_answer='تهران')
            question2 = Question(title='سعدی کجا دفن است', time=30, comment=' ', correct_answer='شیراز')
            question1.groups.append(question_group1)
            question1.groups.append(question_group2)
            question2.groups.append(question_group2)

            course1 = Course(title='first Course',comment='first course commet',time=300 ,price=300000,max_question=5)
            course2 = Course(title='second Course',comment='second course commet',time=400 ,price=200000,max_question=5)
            course1.questions.append(question1)
            course1.questions.append(question2)
            course2.questions.append(question2)

            group2 = Group("group:students")
            group3 = Group("group:editors")
            DBSession.add(group2)
            DBSession.add(group3)
            DBSession.add(question_group1)
            DBSession.add(question_group2)
            DBSession.add(question2)
            DBSession.add(question1)
            DBSession.add(course1)
            DBSession.add(user1)
