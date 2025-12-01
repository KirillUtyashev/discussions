import datetime
from django.test import TestCase
from django.utils import timezone

from payments.models import Subscription, Plan
from users.models import User


def create_plans():
    for i in range(1, 4):
        Plan.objects.create(tariff_type=str(i))


class SubscriptionManagerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_plans()
        cls.user_1 = User.objects.create_user(email='kirill@mail.com', name='Kirill', password='123456')
        cls.user_2 = User.objects.create_user(email='marat@mail.com', name='Marat', password='123456')

    def test_update_subscription(self):
        plan = Plan.objects.get(tariff_type='2')
        now = timezone.localtime(timezone.now())
        Subscription.objects.update_subscription(self.user_1, plan, '123456', now + datetime.timedelta(days=30))
        self.assertEqual(self.user_1.subscriptions.count(), 1)

    def test_week_notice(self):
        plan_1 = Plan.objects.get(tariff_type='1')
        plan_2 = Plan.objects.get(tariff_type='2')
        Subscription.objects.update_subscription(self.user_1, plan_1, '123456', timezone.now() + datetime.timedelta(days=5))
        Subscription.objects.update_subscription(self.user_2, plan_2, '56789', timezone.now() + datetime.timedelta(days=5))
        Subscription.objects.week_notice()
        self.assertEqual(self.user_1.subscriptions.get(active=True).email_warning_date, None)
        self.assertEqual(Subscription.objects.filter(active=True, email_warning_date=None).count(), 2)

    def test_send_email(self):
        plan_1 = Plan.objects.get(tariff_type='1')
        Subscription.objects.update_subscription(self.user_1, plan_1, '123456', datetime.datetime.now())
        res = Subscription.objects.send_week_notice(self.user_1.subscriptions.get(active=True))
        self.assertTrue(res)


