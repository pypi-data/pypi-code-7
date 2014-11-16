from pyramid.response import Response
from pyramid.view import (
    view_config,
    forbidden_view_config,
    )

from pyramid.security import (
    remember,
    forget,
    )

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPForbidden,
    )

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    User,
    Group,
    Question_Group,
    Question,
    Course,
    Exam,
    Answer,
    )

from .jalali import to_jd , jd_to
import transaction
import time


@view_config(route_name='home', renderer='templates/home.pt', permission='view')
def home(request):

    try:
        user = DBSession.query(User).filter(User.login_name == request.authenticated_userid).first()
    except DBAPIError:
        return Response('<html><body>connection error</body></html>', content_type='text/html', status_int=500)
    return {'user':user, 'project': 'vame course'}


@view_config(route_name='course_list', renderer='templates/course_list.pt')
def course_list(request):

    user = DBSession.query(User).filter_by(login_name=request.authenticated_userid).first()

    message = ''
    courses = DBSession.query(Course).all()


    # print(user)
    return {'message':message,'courses':courses, 'user':user}



@view_config(route_name='course_page', renderer='templates/course_page.pt',permission='student')
def course_page(request):
    message = ''

    user = DBSession.query(User).filter_by(login_name=request.authenticated_userid).one()
    course_title = request.matchdict['course_title']
    try:
        course = DBSession.query(Course).filter_by(title=course_title).one()
    except:
        message = 'course not found'
        return {'message':message, 'user':user}

    exams = [exam for exam in user.exams if exam in course.exams]
    can_register = True
    for exam in exams:
        if exam.status != 3: # Not success
            can_register = False


    # print(exams)

    if 'submit' in request.POST and can_register:
        agreement = request.POST.get('agreement')
        if agreement == "agree":


            if user.account > course.price:
                user.account -= course.price
                user.payment += course.price
                if not user.account < 0:


                    exam = Exam(user=user,course=course)
                    # exam.status = 0
                    #  0 registered not started -
                    #  1 registered started not finished
                    #  2 registered started finished not resulted
                    #  3 not success
                    #  4 success


                    # user = DBSession.query(User).filter_by(login_name=request.authenticated_userid).one()
                    # course_title = request.matchdict['course_title']
                    #
                    # course = DBSession.query(Course).filter_by(title=course_title).one()

                    DBSession.add(exam)
                    # exams = [exam for exam in user.exams if exam in course.exams]
                    exams = DBSession.query(Exam).filter_by(user_id=user.id,course_id = course.id)

                    # exams.append(exam)
                    can_register = False

                    message = 'شما در این دوره ثبت نام شدید'

                else:
                    user.account += course.price
                    user.payment -= course.price
                    message = 'اعتبار شما برای شرکت در این دوره کافی نیست. نسبت به افزایش اعتبار خود اقدام کنید'
            else:
                message = 'اعتبار شما برای شرکت در این دوره کافی نیست. نسبت به افزایش اعتبار خود اقدام کنید'

        else:
            message = 'برای شرکت در دوره باید با شرایط شرکت در دوره موافقت کنید'

    return {'message':message,'course':course, 'user':user, 'exams': exams, 'can_register': can_register}




@view_config(route_name='exam_list', renderer='templates/exam_list.pt',permission='student')
def exam_list(request):
    user = DBSession.query(User).filter_by(login_name=request.authenticated_userid).one()
    exams = DBSession.query(Exam).filter_by(user_id=user.id)
    message = ''

    return {'exams':exams,'user':user,'message':message}

@view_config(route_name='exam_page', renderer='templates/exam_page.pt',permission='student')
def exam_page(request):
    user = DBSession.query(User).filter_by(login_name=request.authenticated_userid).one()
    exam_id = request.matchdict['exam_id']
    exam = DBSession.query(Exam).filter_by(id=exam_id).first()
    message = ''


    if not exam in user.exams:
        # return HTTPFound(location=request.route_url('exam_list'))
        return HTTPForbidden()


    #######################################
    elif exam.status == 0: #  0 registered not started - in this case exam question will collected
        message = 'شما هنوز آزمون این دوره را شروع نکرده اید.'
        if 'exam.start' in request.POST:
            import random
            course = exam.course
            temporary_questions = course.questions[:]
            q_number = len(temporary_questions)
            if q_number > course.max_question:
                q_number = course.max_question

            for i in range(q_number):
                q = random.choice(temporary_questions)
                exam.answers.append(Answer(q))
                temporary_questions.remove(q)
            for a in exam.answers:
                DBSession.add(a)
            exam.status = 1
            import time
            exam.start_time = time.time()
            DBSession.add(exam)
            # exam_id = request.matchdict['exam_id']
            exam = DBSession.query(Exam).filter_by(id=exam_id).first()

            message = 'شما در حال آزمون دادن هستید'
            # transaction.commit()


    elif exam.status == 1: #  1 registered started not finished
        message = 'شما در حال آزمون دادن هستید'
        # print('salam')
        if 'exam.finish' in request.POST:
            answers = []
            for a in exam.answers:
                # my_id = a.id
                # print(my_id)
                a.value = request.POST.get(str(a.id), '')
                # print('this is: #########')
                # answers.append(an)
                # print(an)
            if request.POST.get('scored', ''):
                exam.status = 2
                message = 'جواب های شما به آزمون دریافت شد. نتیجه پس از تصحیح اوراق در سایت قرار خواهد گرفت'
            else:
                message = 'جواب های شما ذخیره شد ولی آزمون شما همچنان ادامه دارد'
            DBSession.add(exam)




    elif exam.status == 2: #  2 registered started finished not resulted
        message = 'جواب های شما به آزمون دریافت شد. نتیجه پس از تصحیح اوراق در سایت قرار خواهد گرفت'

    import time
    counter_time = int(exam.course.time - (time.time() - exam.start_time))
    print(counter_time)
    return {'exam':exam, 'message':message, 'user':user, 'counter_time':counter_time}




@view_config(route_name='quiz_start', renderer='templates/quiz_start.pt')
def quiz_start(request):
    return {'quiz': request.matchdict['quiz_id']}


@view_config(route_name='quiz_question', renderer='templates/quiz_question.pt')
def quiz_question(request):
    return {'quiz': request.matchdict['quiz_id'],'question':request.matchdict['question_id']}


@view_config(route_name='quiz_finish', renderer='templates/quiz_finish.pt')
def quiz_finish(request):
    return {'quiz': request.matchdict['quiz_id']}


@view_config(route_name='quiz_result', renderer='templates/quiz_result.pt')
def quiz_result(request):
    return {'quiz': request.matchdict['quiz_id']}


@view_config(route_name='course_add', renderer='templates/course_add.pt', permission='admin')
def course_add(request):
    message = ''
    questions = DBSession.query(Question).all()
    if 'submit' in request.POST:
        question_ids = request.POST.getall('questions')
        title = request.POST.get('title', '')
        comment = request.POST.get('comment', '')
        time = request.POST.get('time', '')
        max_question = request.POST.get('max_question', '')
        min_score = request.POST.get('min_score', '')
        price = request.POST.get('price', '')

        course = Course(title=title,comment=comment,time=time,price=price,max_question=max_question, min_score=min_score)
        for q in questions:
            if str(q.id) in question_ids:
                course.questions.append(q)
        DBSession.add(course)
        message = 'دوره جدید با موفقیت اضافه شد'




    return {'message':message,'questions':questions}

@view_config(route_name='question_add', renderer='templates/question_add.pt', permission='admin')
def question_add(request):
    message = ''
    groups = DBSession.query(Question_Group).all()
    if 'submit' in request.POST:
        question_group_ids = request.POST.getall('groups')
        title = request.POST.get('title', '')
        comment = request.POST.get('comment', '')
        time = request.POST.get('time', '')
        correct_answer = request.POST.get('correct_answer', '')
        # print(question_groups, title,time, correct_answer, comment)
        question = Question(title=title, time=time, comment=comment, correct_answer=correct_answer)
        # question_group_ids = set(question_group_ids)
        for g in groups:
            if str(g.id) in question_group_ids:
                question.groups.append(g)
        DBSession.add(question)
        message = 'سوال جدید با موفقیت اضافه شد'

    return {'message':message, 'groups':groups}


@view_config(route_name='question_group_add', renderer='templates/question_group_add.pt', permission='admin')
def question_group_add(request):
    message = ''
    if 'submit' in request.POST:
        name = request.POST.get('name', '')
        same_groups=DBSession.query(Question_Group).filter_by(title=name).all()
        if not same_groups:
            group = Question_Group(title=name)
            DBSession.add(group)
            message = "گروه جدید سولات با موفقیت اضافه شد"


    return {'message':message}


@view_config(route_name='login', renderer='templates/login.pt')
@forbidden_view_config(renderer='templates/login.pt')
def login(request):

    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = request.route_url('home')

    message = ''

    if 'submit' in request.POST:
        login_name = request.POST.get('login_name', '')
        password = request.POST.get('password', '')

        try:
            user = DBSession.query(User).filter_by(login_name=login_name,password=password).one()
            headers = remember(request, login_name)
            message = 'user logged in:{0}'.format(login_name)
            return HTTPFound(location=referrer, headers=headers)
        # try:
        #     user = DBSession.query(User).filter_by(login_name=login_name,password=password).one()
        #     print(user)
        #     headers = remember(request, login_name)
        #     message = 'user logged in:{0}'.format(user.first_name)
        #     return HTTPFound(location=referrer, headers=headers)
        except:
            message = 'کاربر پیدا نشد'

    return {'user':request.authenticated_userid, 'message':message}

@view_config(route_name='logout', renderer='templates/logout.pt')
def logout(request):
    headers = forget(request)
    return HTTPFound(location=request.route_url('home'), headers=headers)


@view_config(route_name='signup', renderer='templates/signup.pt')
def signup(request):
    message = ''
    #groups = DBSession.query(Group).all()
    if 'submit' in request.POST:
        same_users=DBSession.query(User).filter_by(login_name=request.POST.get('login_name', '')).all()
        if not same_users:
            user = User(login_name=request.POST.get('login_name', ''),
                        first_name=request.POST.get('first_name', ''),
                        last_name=request.POST.get('last_name', ''),
                        password=request.POST.get('password', ''),
                        email=request.POST.get('email', ''),
                        phone = request.POST.get('phone', ''),
                        mobile = request.POST.get('mobile', ''),)

            student_group = DBSession.query(Group).filter_by(title='group:students').one()

            user.groups.append(student_group)

            DBSession.add(user)
            message ='کاربر ثبت شد'
        else:
            message ='امکان ثبت کاربر وجود ندارد'




    return {
        'login_name':request.POST.get('login_name', ''),
        'first_name':request.POST.get('first_name', ''),
        'last_name':request.POST.get('last_name', ''),
        'password':request.POST.get('password', ''),
        'email':request.POST.get('email', ''),
        'phone':request.POST.get('phone', ''),
        'mobile':request.POST.get('mobile', ''),
        'message':message
            }

@view_config(route_name='profile', renderer='templates/profile.pt', permission='student')
def profile(request):
    # this page is profile of user
    return {}


@view_config(route_name='certificate', renderer='templates/certificate.pt', permission='view')
def certificate(request):
    # exam = request.matchdict['exam_id']
    # course = request.matchdict['course_title']
    exam = DBSession.query(Exam).filter_by(id=request.matchdict['exam_id'], status=4).first()
    # this page is profile of user

    return {'exam':exam}


@view_config(route_name='payment', renderer='templates/payment.pt', permission='student')
def payment(request):
    user = DBSession.query(User).filter_by(login_name=request.authenticated_userid).one()
    message = ''
    print('test1')
    if 'submit' in request.POST:
        print('test')
        amount = int(request.POST.get('amount',0))
        if amount > 0:
            user.account += amount
            # transaction.commit()
            DBSession.add(user)
            message = 'اکانت با موقیت افزایش یافت'
        else:
            message = 'خطایی در افزایش حساب کاربری اتفاق افتاد'


    # for i in request.POST.items
    return {'message':message, 'user': user}


@view_config(route_name='score_exam_list', renderer='templates/score_exam_list.pt', permission='edit')
def score_exam_list(request):
    message = ''
    status = 2
    if 'submit.status' in request.POST:
        status = int(request.POST.get('status','2'))
    exams = DBSession.query(Exam).filter_by(status=status).all()
    return {'exams':exams}

@view_config(route_name='score_exam_page', renderer='templates/score_exam_page.pt', permission='edit')
def score_exam_page(request):
    message = ''
    exam_id = int(request.matchdict['exam_id'])
    exam = DBSession.query(Exam).filter_by(id=exam_id).first()
    true_answer = 0
    if 'submit' in request.POST:
        for a in exam.answers:

            a.score = int(request.POST.get(str(a.id), a.score))
            if a.score == 2:
                true_answer += 1


        if request.POST.get('scored', ''):

            print(true_answer, len(exam.answers), exam.course.min_score ,'===', true_answer / len(exam.answers), (exam.course.min_score / 100))
            if (true_answer / len(exam.answers) >= (exam.course.min_score / 100)) :
                exam.status = 4
            else:
                exam.status = 3

        DBSession.add(exam)
        transaction.commit()

    exam = DBSession.query(Exam).filter_by(id=exam_id).first()
        # for a in exam.answers:
        #     print(a.find_score(),a.score)


    return {'exam':exam}


