from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = 'Создает юзера с данными параметрами'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str)
        parser.add_argument('password', type=str)
        parser.add_argument('name', type=str)

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        name = options['name']
        User.objects.create_user(email=email, password=password, name=name)
