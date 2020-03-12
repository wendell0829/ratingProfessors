from .utils import success, params_error, check_register, add_session, \
    check_session,  login_required, round_up, create_rating_record, get_current_user
from .models import User, models, Session, ModuleInstance, RatingRecord, \
    Professor, Module
import uuid
import json
from django.db.models import Avg


@check_session
def login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    try:
        user = User.objects.get(username=username)
    except models.ObjectDoesNotExist:
        user = None
    if user:
        if user.password == password:
            session_key = request.GET.get('session_key')
            add_session(session_key, {'username': user.username})
            return success(message='Successfully signed in')
        else:
            return params_error(message='Incorrect password')
    else:
        return params_error(message='User does not exist')


@check_session
def register(request):
    username = request.POST.get('username')
    password1 = request.POST.get('password1')
    password2 = request.POST.get('password2')
    email = request.POST.get('email')

    error_message = check_register(email, username, password1, password2)

    if error_message:
        return params_error(message=error_message)
    else:
        User.objects.create(username=username, email=email, password=password1)
        return success('Successfully registered')


@check_session
@login_required
def logout(request):
    session_key = request.GET.get('session_key')
    session = Session.objects.get(key=session_key)
    session_data = json.loads(session.data)
    if 'username' in session_data.keys():
        del session_data['username']
        session.data = json.dumps(session_data)
        session.save()
        return success(message='Successfully logout')
    else:
        return params_error(message='You are not signed in')


def session(request):
    session_key = str(uuid.uuid4()).replace('-', '')
    session_data = {}
    Session.objects.create(key=session_key, data=session_data)
    return success(data={'session_key': session_key})


@check_session
@login_required
def modules_list(request):
    module_instance_objects = ModuleInstance.objects.all()
    module_instances = []
    for module_instance_object in module_instance_objects:
        professors = []
        for professor in module_instance_object.professors.all():
            professors.append(professor.id + ',' + professor.name)

        module_instance = {}
        module_instance['module_code'] = module_instance_object.module.code
        module_instance['module_name'] = module_instance_object.module.name
        module_instance['year'] = module_instance_object.year
        module_instance['semester'] = module_instance_object.semester
        module_instance['professors'] = professors

        module_instances.append(module_instance)

    print(module_instances)
    return success(data={'module_instances': module_instances})


@check_session
@login_required
def ratings_view(request):
    rating_records = RatingRecord.objects.values('professor').annotate(rating=Avg('rating'))
    ratings = list(rating_records)
    for rating in ratings:
        professor_id = rating['professor']
        rating['professor_name'] = Professor.objects.get(id=professor_id).name
        rating['rating'] = round_up(rating['rating'])
    return success(data={'ratings': ratings})


@check_session
@login_required
def ratings_avg(request):
    professor_id = request.GET.get('professor_id')
    module_code = request.GET.get('module_code')
    try:
        professor = Professor.objects.get(id=professor_id)
        module = Module.objects.get(code=module_code)
    except:
        professor = None
        module = None

    if not (professor and module):
        return params_error(message='please provide a valid professor id and a valid module code')

    rating = RatingRecord.objects.filter(professor__id=professor_id).\
        filter(module_instance__module__code=module_code).aggregate(avg_rating=Avg('rating'))['avg_rating']
    rating = round_up(rating)

    print(rating)
    return success(data={
        'rating': rating,
        'professor_name': professor.name,
        'module_name': module.name,
    })


@check_session
@login_required
def ratings_rate(request):
    professor_id = request.POST.get('professor_id')
    module_code = request.POST.get('module_code')
    year = request.POST.get('year')
    semester = request.POST.get('semester')
    rating = request.POST.get('rating')
    user = get_current_user(request)
    print(professor_id)
    print(module_code)
    print(year)
    print(semester)
    print(rating)
    try:
        professor = Professor.objects.get(id=professor_id)
        module = Module.objects.get(code=module_code)
        print(professor, module)
    except:
        return params_error(message='Please provide a valid professor id and a valid module code')

    message = create_rating_record(module, professor, year, semester, rating, user)
    if message:
        return params_error(message=message)
    else:
        return success(message='Successfully rated on professor {}({})'.format(
            professor.name, professor_id
        ))
