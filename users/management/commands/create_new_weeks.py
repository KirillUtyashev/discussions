from django.core.management.base import BaseCommand
from users.tasks import create_new_weeks


class Command(BaseCommand):
    help = 'Чистит бд'

    def handle(self, *args, **kwargs):
        create_new_weeks()

