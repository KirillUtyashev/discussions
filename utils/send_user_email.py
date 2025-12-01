from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string


def send_user_email(subject, template_name, emails: list, parameters):
    email = render_to_string(template_name, parameters)
    text = strip_tags(email)
    send_mail(subject, message=text, from_email='Команда Дискуссии.ру <support@discussions.ru>',
              recipient_list=emails, html_message=email, fail_silently=False)
