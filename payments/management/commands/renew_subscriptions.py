from django.core.management.base import BaseCommand
from payments.actions import renew_subscriptions


class Command(BaseCommand):
    help = 'Создает базовые планы'

    def handle(self, *args, **kwargs):
        renew_subscriptions()
