from .models import Course, User
from DilemmaPlatform.celery import app
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from .tokens import account_activation_token
from utils.send_user_email import send_user_email


def create_new_weeks():
    for course in Course.objects.all():
        course.create_new_week()


@app.task
def send_password_reset_email(email):
    template_name = 'users/password_reset_email.html'
    user = User.objects.get(email=email)
    subject = 'Восстановление пароля'
    link = 'https://discussions.ru/' + f'{urlsafe_base64_encode(force_bytes(user.pk))}/' + f'{default_token_generator.make_token(user)}/'
    parameters = {
        'message': 'Нажмите на кнопку чтобы сбросить пароль:',
        'link': link
    }
    send_user_email(subject, template_name, [user.email], parameters)


@app.task
def send_registration_email(email):
    template_name = 'users/registration_email.html'
    user = User.objects.get(email=email)
    subject = 'Давайте дискутировать!'
    parameters = {
        'message': 'Вы стали частью семьи Дискуссии.ру. Пожалуйста, перейдите по ссылке ниже, чтобы подтвердить Вашу почту.',
        'link': 'https://discussions.ru/activate/' +
                f'{urlsafe_base64_encode(force_bytes(user.pk))}/' + f'{account_activation_token.make_token(user)}/'
    }
    send_user_email(subject, template_name, [user.email], parameters)


@app.task
def send_verification_email(email):
    template_name = 'users/verification_email.html'
    user = User.objects.get(email=email)
    subject = 'Подтвердите почту на сайте Дискуссии.ру'
    parameters = {
        'message': 'Пожалуйста, перейдите по ссылке ниже, чтобы подтвердить Вашу почту.',
        'link': 'https://discussions.ru/activate/' +
                f'{urlsafe_base64_encode(force_bytes(user.pk))}/' + f'{account_activation_token.make_token(user)}/'
    }
    send_user_email(subject, template_name, [user.email], parameters)

