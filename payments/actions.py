import datetime
import json
import os
from hashlib import sha256
import requests
from django.utils import timezone
from .tasks import new_subscription_email
from payments.models import Order, Subscription

TERMINAL_KEY = os.environ.get('TERMINAL_KEY')
TERMINAL_PASSWORD = os.environ.get('TERMINAL_PASSWORD')


def generate_token(password, params) -> str:
    copy_params = params.copy()
    copy_params['Password'] = password
    result = ''
    sorted_keys = sorted(copy_params.keys())
    for key in sorted_keys:
        result += str(copy_params[key])
    token = sha256(result.encode('utf-8')).hexdigest()
    return token


def initpayment(user, plan, order, first_payment=False):
    try:
        current_subscription = Subscription.objects.get(user=user, active=True)
        if current_subscription.plan.price == plan.price and first_payment:
            return '1'
        if first_payment:
            price = plan.calculate_price_to_pay(current_subscription.expires, current_subscription.plan.price)
        else:
            price = plan.price
    except Subscription.DoesNotExist:
        price = plan.price
    parameters = {
        'TerminalKey': TERMINAL_KEY,
        'Amount': price,
        'OrderId': order.order_id,
        'Description': 'Подписка на платформе Дискуссии.ру'
    }
    if first_payment:
        extra = {
            'Recurrent': 'Y',
            'CustomerKey': str(user.id)
        }
        parameters.update(extra)
    parameters['Token'] = generate_token(TERMINAL_PASSWORD, parameters)
    parameters.update({'DATA': {
        'Email': user.email
    },
        'Receipt': {
            'Email': user.email,
            'EmailCompany': 'contact@discussions.ru',
            'Taxation': 'usn_income',
            'Items': [{
                "Name": plan.get_tariff_type_display(),
                "Price": price,
                "Quantity": 1.00,
                "Amount": price,
                "PaymentMethod": "full_prepayment",
                "PaymentObject": "service",
                "Tax": "none"
            }]
        }
    })
    response = requests.post("https://securepay.tinkoff.ru/v2/Init",
                             data=json.dumps(parameters), headers={'Content-Type': 'application/json'})
    return json.loads(response.content)


def renew_subscriptions():
    # Сначала находим отмененные подписки и отменяем их
    Subscription.objects.filter(expires__lte=datetime.datetime.now(), active=True, renewal=False).update(active=False)
    # Теперь ищем активные подписки, у которых истек срок
    res = Subscription.objects.filter(expires__lte=datetime.datetime.now(), renewal=True)
    for subscription in res:
        order = Order.objects.create(user=subscription.user, plan_id=subscription.plan.tariff_type, status='RENEW')
        init_out = initpayment(subscription.user, subscription.plan, order)
        charge(subscription.rebill_id, init_out['PaymentId'])


def charge(rebill_id, paymentid):
    parameters = {
        'TerminalKey': TERMINAL_KEY,
        'PaymentId': paymentid,
        'RebillId': rebill_id,
    }
    parameters['Token'] = generate_token(TERMINAL_PASSWORD, parameters)
    requests.post("https://securepay.tinkoff.ru/v2/Charge",
                  data=json.dumps(parameters), headers={'Content-Type': 'application/json'})


def process_response(rebill_id, order, status):
    if status == 'CONFIRMED':
        expiry_date = timezone.now() + datetime.timedelta(days=30)
        if order.status == 'NEW':
            try:
                Subscription.objects.filter(user=order.user, active=True).update(active=False, renewal=False)
            except Subscription.DoesNotExist:
                pass
            Subscription.objects.create(user=order.user, plan=order.plan, expires=expiry_date, rebill_id=rebill_id)
            new_subscription_email.delay(order.user.id, order.plan.name, 'payments/new_subscription.html')
        elif order.status == 'RENEW':
            try:
                # Первый автоплатеж, который прошел успешно
                a = Subscription.objects.filter(user=order.user, plan=order.plan, active=True).update(expires=expiry_date, email_warning_date=expiry_date - datetime.timedelta(days=7))
            except Subscription.DoesNotExist:
                # N-ая попытка провести автоплатеж, подписка заморожена, необходимо найти последний план
                Subscription.objects.filter(user=order.user, plan=order.plan).last().update(expires=expiry_date, email_warning_date=expiry_date - datetime.timedelta(days=7), active=True)
        order.delete()
    elif status == 'REJECTED':
        # Оплата прошла неуспешно, необходимо заморозить подписку, если рекурентный платеж
        if order.status == 'RENEW':
            try:
                Subscription.objects.filter(user=order.user, active=True, plan=order.plan).update(active=False)
            # Если уже поменяли, то ничего не делаем
            except Subscription.DoesNotExist:
                pass
        order.delete()
