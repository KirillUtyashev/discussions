from django.core.management.base import BaseCommand
from django.utils import timezone
from payments.models import Plan


class Command(BaseCommand):
    help = 'Создает базовые планы'

    def handle(self, *args, **kwargs):
        for i in range(1, 4):
            Plan.objects.create(tariff_type=str(i))
