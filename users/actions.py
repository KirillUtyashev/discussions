import string
import random
from django.contrib.auth import authenticate, get_user_model, login, \
    update_session_auth_hash
from django.core.cache import cache
from .tasks import (send_password_reset_email, send_registration_email,
                    send_verification_email)
from django.http import JsonResponse
from notifications.models import Notification
from users.forms import EmailChangeForm, UserPasswordChangeForm
from users.helper_functions import negative_response
from users.models import Course, User
from django.conf import settings

SITENAME = settings.SITENAME


def generate_default_data(request):
    all_courses = Course.objects.get_all_user_courses(request.user)
    student_count = request.user.count_all_unique_students()
    if request.user.subscriptions.filter(active=True).exists():
        max_students_allowed = request.user.subscriptions.get(active=True).plan.number_of_unique_students_allowed
        plan = request.user.subscriptions.last().plan.name
    else:
        max_students_allowed = 30
        plan = 'Стартер'

    data = {
        'name': request.user.name,
        'email': request.user.email,
        'student_count': student_count,
        'plan': plan,
        'courses': all_courses,
        'sitename': SITENAME,
        'max_students_allowed': max_students_allowed,
        'unread_notifications': Notification.objects.user_unread_count(request.user)}
    return data


def generate_unique_code() -> str:
    """
    Генерация уникального кода курса.
    """
    code = ''
    for _ in range(7):
        code += random.choice(string.ascii_lowercase + string.digits)
    try:
        Course.objects.get(code=code)
        return generate_unique_code()
    except Course.DoesNotExist:
        return code


def register_user(email, name, password):
    """
    Регистрация юзера. Гарантированно, что юзер не существует. По дефолту, всем
    новым юзерам при регистрации даем "Стартер" тарифный план.
    1 - успех
    """
    get_user_model().objects.create_user(email=email, name=name, password=password)


def add_user(course, user):
    """
    Добавление юзера на курс в качестве студента. Гарантировано, что юзер не админ курса
    и вверно ввел все данные для входа.
    1 - успез
    """
    if course.author.subscriptions.filter(active=True).exists():
        unique_students_allowed = course.author.subscriptions.get(active=True).plan.number_of_unique_students_allowed
    else:
        unique_students_allowed = 30
    current_number_of_students = course.author.count_all_unique_students()
    if current_number_of_students == unique_students_allowed:
        return JsonResponse({'message': '6'})
    course.students.add(user)
    cache.delete(f'students_{course.code}')
    cache.delete(f'{user.id}_courses')
    return JsonResponse({
        'message': '1',
        'course_url': course.get_absolute_url()
    })


def reset_password(email):
    if not User.objects.filter(email=email).exists():
        return JsonResponse({
            'message': '0'
        })
    send_password_reset_email.delay(email)
    return JsonResponse({
        'message': '1'
    })


def send_confirmation_email(email):
    send_verification_email.delay(email)


def join_course(request):
    """
    Добавить юзера на курс в качестве студента.
    5 - неверный пароль курса
    4 - уже добавлен курс
    3 - юзер является админом курса
    2 - нужен пароль курса
    1 - успех
    0 - курса не существует
    """
    course_code = request.POST.get('code').lower()
    try:
        course = Course.objects.get(code=course_code)
        if course.is_demo:
            return JsonResponse({
                'message': '0'
            })
        if course.password is None:
            if request.user.id == course.author_id or course.instructors.filter(id=request.user.id).exists():
                return JsonResponse({
                    'message': '3'
                })
            else:
                if course.students.filter(id=request.user.id).exists():
                    return JsonResponse({
                        'message': '4'
                    })
                else:
                    return add_user(course, request.user)
        else:
            user_input_password = request.POST.get('password')
            if user_input_password == '':
                return JsonResponse({
                    'message': '2'
                })
            else:
                if course.password == user_input_password:
                    return add_user(course, request.user)
                else:
                    return JsonResponse({
                        'message': '5'
                    })
    except Course.DoesNotExist:
        return JsonResponse({
            'message': '0'
        })


def create_course(request):
    """
    Создать курс.
    1 - успех
    0 - курс с таким именем у данного юзера есть
    """
    course_name = request.POST.get('name')
    if Course.objects.filter(name=course_name, author_id=request.user.id).exists():
        return JsonResponse({
            'message': '0'
        })
    else:
        course = Course.objects.create(name=course_name, code=generate_unique_code(), author=request.user)
        cache.delete(f'{request.user.id}_courses')
        return JsonResponse({
            'message': '1',
            'course_url': course.get_settings_url()
        })


def change_password(request):
    """
    Поменять пароль.
    """
    form = UserPasswordChangeForm(request.user, request.POST)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return JsonResponse({
            'message': '1'
        })
    else:
        if form.errors:
            try:
                message = form.errors.as_data()['old_password'][0].message
                return JsonResponse({'message': message})
            except KeyError:
                message = form.errors.as_data()['new_password2'][0].message
                return JsonResponse({'message': message})
        else:
            return JsonResponse({'message': -1})


def change_email(request):
    """
    Поменять почту.
    """
    form = EmailChangeForm(request.user, request.POST)
    if form.is_valid():
        form.save()
        user = request.user
        user.email_is_verified = False
        user.save(update_fields=['email_is_verified'])
        send_confirmation_email(user.email)
        return JsonResponse({
            'message': '1'
        })
    else:
        return JsonResponse({
            'message': '0'
        })


def change_profile(request):
    """
    Поменять имя в профиле.
    """
    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        return negative_response()
    user.change_name(request.POST.get('new_name'))
    return JsonResponse({
        'message': '1'
    })


def unenroll(request):
    """
    Выйти из курса.
    """
    try:
        course = Course.objects.get(id=request.POST.get('id'))
    except Course.DoesNotExist:
        return negative_response()
    res = Course.objects.unenroll(course, request.user)
    return JsonResponse({
        'message': res
    })


def switch_renewal(renewal, user):
    if renewal == '0':
        user.subscriptions.filter(active=True).update(renewal=False)
    elif renewal == '1':
        user.subscriptions.filter(active=True, renewal=False).update(renewal=True)
    else:
        return negative_response()
