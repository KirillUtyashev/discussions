from .actions import renew_subscriptions
from payments.models import Subscription


def send_week_notice_email():
    Subscription.objects.week_notice()


def daily_renewal_subscriptions():
    renew_subscriptions()
