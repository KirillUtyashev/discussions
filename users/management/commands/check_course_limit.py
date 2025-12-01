from datetime import timedelta
import pytz
from django.core.management.base import BaseCommand
from django.utils import timezone

from payments.models import Subscription
from users.actions import generate_unique_code
from users.models import Course, User


class Command(BaseCommand):
    help = 'Проверка ограничения'

    def handle(self, *args, **kwargs):
        author = User.objects.create_user(name='Главный', email='main@mail.ru', password='123456')
        course = Course.objects.create(name='MAT135', code=generate_unique_code(), author=author)
        time = timezone.localtime(timezone.now())
        expires = time + timedelta(seconds=10)
        a = Subscription.objects.create(user=author, plan_id='1', expires=expires)
        for i in range(31):
            cur = User.objects.create_user(name=i, email=f'{i}@mail.ru', password='123456')
            course.students.add(cur)


