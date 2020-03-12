import json
from django.shortcuts import HttpResponse
from .models import User, models, Session, ModuleInstance, RatingRecord
from functools import wraps


def restful_response(code, message, data):
    return HttpResponse(json.dumps({'code': code, 'message': message, 'data': data}))


def success(message="", data=None):
    return restful_response(200, message, data)


def params_error(message="", data=None):
    return restful_response(400, message, data)


def check_username(username):
    if not username:
        return 'Please provide a username'

    if len(username) == 0:
        return 'Please provide a username'

    if len(username) > 20:
        return 'The length of username should not be longer than 20'

    try:
        user = User.objects.get(username=username)
    except models.ObjectDoesNotExist:
        user = None

    if user:
        return 'The username has been registered'


def check_email(email:str):
    if not email:
        return 'Invalid email address'
    if '@' not in email or len(email) > 50:
        return 'Invalid email address'
    else:
        email_name = email.split('@')[0]
        email_app = email.split('@')[1]
        if '.com' not in email_app or len(email_app)<=4 or len(email_name)==0:
            return 'Invalid email address'

    user = None
    try:
        user = User.objects.get(email=email)
    except models.ObjectDoesNotExist:
        pass
    if user:
        return 'Email has been registered'


def check_password(password1, password2):
    if not password1:
        return 'Please provide a password'
    if password1 != password2:
        return 'Passwords do not match'
    elif len(password1) == 0:
        return 'Please provide a password'
    elif len(password1) > 20:
        return 'The length of password should not be longer than 20'


def check_register(email, username, password1, password2):
    error_message = [check_username(username), check_email(email), check_password(password1, password2)]
    while None in error_message:
        error_message.remove(None)
    if len(error_message) > 0:
        return error_message[0]


def add_session(session_key, add_data):
    session = Session.objects.get(key=session_key)
    session_data = json.loads(session.data)
    session_data.update(add_data)
    session_data = json.dumps(session_data)
    session.data = session_data
    session.save()


def check_session(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            session_key = request.GET.get('session_key')
            print(session_key)
            session = Session.objects.get(key=session_key)
            print(session)
        except:
            return params_error('Connection lost, please restart your client application')
        return func(request, *args, **kwargs)
    return wrapper


def login_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        session_key = request.GET.get('session_key')
        session = Session.objects.get(key=session_key)
        session_data = json.loads(session.data)
        try:
            current_user_name = session_data.get('username')
        except:
            current_user_name = None
        if current_user_name:
            return func(request, *args, **kwargs)
        else:
            return params_error(message='please login first')

    return wrapper


def get_current_user(request):
    session_key = request.GET.get('session_key')
    session = Session.objects.get(key=session_key)
    session_data = json.loads(session.data)
    try:
        current_user_name = session_data.get('username')
        current_user = User.objects.get(username=current_user_name)
    except:
        current_user = None
    return current_user


def round_up(a):
    if (a-0.5)%2 == 0:
        return int(a+1)
    else:
        return round(a)


def create_rating_record(module, professor, year, semester, rating, user):
    module_instance = ModuleInstance.objects.filter(module=module). \
        filter(year=year).filter(semester=semester)
    if len(module_instance) == 1:
        module_instance = module_instance[0]
    else:
        return 'The module instance does not exist'

    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            return 'Please provide a valid rating(between 1-5)'
    except:
        return 'Please provide a valid rating(between 1-5)'

    if professor not in module_instance.professors.all():
        return 'Professor {}({}) does not teach {}({}) in {} semester {}'.format(
            professor.name, professor.id, module.name, module.code, year, semester
        )

    RatingRecord.objects.create(
        module_instance=module_instance,
        professor=professor,
        rating=rating,
        user=user,
    )
