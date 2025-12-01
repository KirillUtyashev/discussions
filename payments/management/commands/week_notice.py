from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from payments.models import Subscription
from users.actions import generate_unique_code
from users.models import Course, User


class Command(BaseCommand):
    help = 'Проверка ограничения'

    def handle(self, *args, **kwargs):
        # user = User.objects.create_user(name='Kirill', email='kirillut04@gmail.com', password='123456')
        # Subscription.objects.create(user=user, plan_id='1', expires=timezone.localtime(timezone.now()) + timedelta(days=5))
        Subscription.objects.week_notice()
