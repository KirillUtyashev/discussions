import datetime
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from utils.send_user_email import send_user_email
from users.models import Course


class SubscriptionManager(models.Manager):
    email_template_name = 'payments/warning.html'

    def create(self, **obj_data):
        obj_data['email_warning_date'] = obj_data['expires'] - datetime.timedelta(days=7)
        super().create(**obj_data)
        Course.objects.update_access(obj_data['user'])

    def week_notice(self):
        res = self.exclude(email_warning_date__isnull=True).filter(email_warning_date__lte=datetime.datetime.now(), renewal=True)
        for subscription in res:
            if self.send_week_notice(subscription):
                subscription.email_warning_date = None
                subscription.save(update_fields=['email_warning_date'])

    def send_week_notice(self, subscription):
        user = subscription.user
        expiration_date = subscription.expires.strftime('%d %B %Y')
        subject = f'Автоматическое продление подписки'
        parameters = {
            'message': f'Ваша подписка автоматически продлится через 7 дней, {expiration_date}.\nЕсли Вы хотите отменить подписку, перейдите по ссылке:'
        }
        send_user_email(subject, self.email_template_name, [user.email], parameters)
        return True
