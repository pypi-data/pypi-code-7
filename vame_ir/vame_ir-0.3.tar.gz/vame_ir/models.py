from pyramid.security import (
    Allow,
    Everyone,
)
from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    String,
    Table,
    ForeignKey,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

user_2_group_map = Table('user_2_group_map', Base.metadata,
                       Column('user_id', Integer, ForeignKey('users.id')),
                       Column('group_id', Integer, ForeignKey('groups.id'))
)




class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login_name = Column(String(50))
    password = Column(String(50),nullable=False)
    first_name = Column(String(50),nullable=False)
    last_name = Column(String(50),nullable=False)
    email = Column(String(50),nullable=False)
    phone = Column(String(50),nullable=False)
    mobile = Column(String(50),nullable=False)
    payment = Column(Integer)
    account = Column(Integer)
    blocked = Column(Integer) # 0 for no - null or -1 for not activated yet - bigger than 1 for yes

    groups = relationship('Group',
                          secondary=user_2_group_map,
                          backref='users'
                          )

    exams = relationship('Exam',backref='user')

    def __init__(self, login_name, password, first_name='temp', last_name = 'temp', email = 'temp',
                 phone = '0123456', mobile = '0123456'):
        self.login_name = login_name
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.mobile = mobile
        self.blocked = -1
        self.payment = 0
        self.account = 0
        #self.account

    def __repr__(self):
        return "<User('{0}','{1}','{2}')>".format(self.login_name, self.first_name, self.last_name)


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    title = Column(String(50))

    def __init__(self, title=''):
        self.title = title

    def __repr__(self):
        return "<Group('{0}')>".format(self.title)



question_2_course_map = Table('question_2_course_map', Base.metadata,
                       Column('question_id', Integer, ForeignKey('questions.id')),
                       Column('course_id', Integer, ForeignKey('courses.id'))

)

#Course use as a framework for exam so it have one to many ralation with exam
#it also have a many to many relation with user
class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    title = Column(String(50), unique=True)
    comment = Column(Text)
    time = Column(Integer)
    price = Column(Integer)
    max_question = Column(Integer)
    min_score = Column(Integer)


    exams = relationship('Exam',backref='course')

    def __init__(self, title = '', comment = '', time = '', price = '', max_question = '', min_score = 50):
        self.title = title
        self.comment = comment
        self.time = time
        self.price = price
        self.max_question = max_question
        self.min_score = min_score


#this have a many to one ralation with user exam will be create when user want to star exam of cource
class Exam(Base):
    __tablename__ = 'exams'
    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    comment = Column(Text)
    # submit_time = Column(Integer)

    submit_time = Column(Integer)
    status = Column(Integer)
    max_question = Column(Integer)

    # 0 registered not started -
    #  1 registerid started not finished
    #  2 registerid started finished not resulted
    #  3 not successd
    #  4 successd
    start_time = Column(Integer)
    payment = Column(Integer) #True or False
    answers = relationship('Answer', backref='exam')
     # = relationship('Answer',backref='question')

    user_id = Column(Integer,ForeignKey('users.id'))
    course_id = Column(Integer,ForeignKey('courses.id'))


    def __init__(self, user=None, course=None, comment=''):
        if user:
            self.user = user
        if course:
            self.course = course
            self.time = course.time
            self.max_question = course.max_question
        import time
        self.status = 0
        self.start_time = 0
        self.comment = comment
        self.submit_time = int(time.time())


    def status_finder(self):
        if self.status == 0:
            return 'ثبت نام شده'
        elif self.status == 1:
            return 'آزمون شروع شده'
        elif self.status == 2:
            return 'جواب آزمون مشخص نشده'
        elif self.status == 3:
            return 'رد شده'
        elif self.status == 4:
            return 'قبول'
        else:
            return 'نا مشخص'

    def gdate(self):
        import datetime
        d = datetime.date.fromtimestamp(self.start_time)
        return d






#this have a many to many relation with exam 


question_2_question_group_map = Table('question_2_question_group_map', Base.metadata,
                       Column('question_id', Integer, ForeignKey('questions.id')),
                       Column('group_id', Integer, ForeignKey('question_groups.id'))

)

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    type = Column(String(50))
    title = Column(String(50))
    time = Column(Integer)
    comment = Column(String(50))
    correct_answer = Column(String(50))
    user_answer = Column(String(50))

    groups = relationship('Question_Group',
                          secondary=question_2_question_group_map,
                          backref='questions'
                          )

    courses = relationship('Course',
                          secondary=question_2_course_map,
                          backref='questions'
                          )

    answers = relationship('Answer',backref='question')

    def __init__(self, type='', title='', time='', comment='', correct_answer='', groups=[]):
        self.type = type
        self.title = title
        self.time = time
        self.comment = comment
        self.correct_answer = correct_answer
        for group in groups:
            if group not in self.groups:
                self.groups.append(group)


    def __repr__(self):
        return "<Question('{0}')>".format(self.title)


class Question_Group(Base):
    __tablename__ = 'question_groups'

    id = Column(Integer, primary_key=True)
    title = Column(String(50))

    def __init__(self, title=''):
        self.title = title

    def __repr__(self):
        return "<Question_Group('{0}')>".format(self.title)


class Answer(Base):
    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True)
    value = Column(Text)
    score = Column(Integer)


    exam_id = Column(Integer, ForeignKey('exams.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))

    def __init__(self, question):
        self.question = question
        self.value = ''
        # self.value = value

    def find_score(self):
        if self.score == 0:
            return 'تصحیح نشده'
        elif self.score == 1:
            return 'پاسخ غلط'
        elif self.score == 2:
            return 'پاسخ صحیح'
        else:
            return 'نا مشخص'









Index('user_index', User.login_name, unique=True, mysql_length=50)
