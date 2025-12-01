import datetime
from django.test import TestCase, override_settings

import DilemmaPlatform
from payments.actions import renew_subscriptions
from payments.models import Subscription, Plan
from payments.tests.test_managers import create_plans
from users.models import User


class TestActions(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_plans()
        cls.user_1 = User.objects.create_user(email='kirill@mail.com', name='Kirill', password='123456')
        cls.user_2 = User.objects.create_user(email='marat@mail.com', name='Marat', password='123456')

    def test_renew_subscriptions(self):
        plan_1 = Plan.objects.get(tariff_type='1')
        Subscription.objects.create(user=self.user_1, plan=plan_1, rebill_id='123456', expires=datetime.datetime.now() - datetime.timedelta(minutes=10))
        renew_subscriptions()
        self.assertEqual(self.user_1.subscriptions.count(), 2)
