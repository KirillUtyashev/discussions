import time
from django.utils import timezone
from django.db import models
import datetime
from payments.managers import SubscriptionManager
from users.models import User


class Order(models.Model):
    order_id = models.CharField(primary_key=True)
    status = models.CharField(default='NEW')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    plan = models.ForeignKey('Plan', on_delete=models.CASCADE, related_name='orders')

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = str(self.user.id) + str(int(time.time()))
        super().save(*args, **kwargs)


class Plan(models.Model):
    class TariffType(models.TextChoices):
        BASIC = '1', 'BASIC'
        PRO = '2', 'PRO'
        ADVANCED = '3', 'ADVANCED'
        ENTERPRISE = '4', 'ENTERPRISE'
    tariff_type = models.CharField(max_length=1, choices=TariffType.choices, primary_key=True)
    price = models.IntegerField()
    name = models.CharField(max_length=255, blank=True, null=True)
    for_whom = models.CharField(max_length=255, blank=True, null=True)
    number_of_unique_students_allowed = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.price:
            if self.tariff_type == '1':
                self.price = 249 * 100
                self.name = 'Базовый'
                self.for_whom = 'Для классов'
                self.number_of_unique_students_allowed = 100
            elif self.tariff_type == '2':
                self.price = 449 * 100
                self.name = 'Оптимальный'
                self.for_whom = 'Для курсов'
                self.number_of_unique_students_allowed = 300
            elif self.tariff_type == '3':
                self.price = 999 * 100
                self.name = 'Продвинутый'
                self.for_whom = 'Для онлайн-курсов'
                self.number_of_unique_students_allowed = 500
        super().save(*args, **kwargs)

    def price_rubles(self):
        return str(self.price // 100) + ' ₽'

    def calculate_price_to_pay(self, date, price2):
        time_dif = (date - timezone.now()).days
        money_left = price2 * time_dif / 30
        price = int(self.price - money_left)
        return price


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    active = models.BooleanField(default=True)
    expires = models.DateTimeField()
    renewal = models.BooleanField(default=True)
    rebill_id = models.CharField(max_length=255, blank=True, null=True)
    email_warning_date = models.DateTimeField(blank=True, null=True)
    plan = models.ForeignKey('Plan', on_delete=models.CASCADE, related_name='subscriptions')
    objects = SubscriptionManager()

    class Meta:
        ordering = ['-expires']


class DebugMessage(models.Model):
    message = models.TextField()
