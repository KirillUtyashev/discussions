from django.core.management.base import BaseCommand

from users.models import Course, User


class Command(BaseCommand):
    help = 'Чистит бд'

    def handle(self, *args, **kwargs):
        User.objects.all().delete()
        Course.objects.all().delete()
