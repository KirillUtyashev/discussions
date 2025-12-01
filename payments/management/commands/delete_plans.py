from django.core.management.base import BaseCommand
from django.utils import timezone
from payments.models import Plan


class Command(BaseCommand):
    help = 'Создает базовые планы'

    def handle(self, *args, **kwargs):
        Plan.objects.all().delete()
