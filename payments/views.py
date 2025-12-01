import json
import os
import datetime

from notifications.actions import show_notifications
from notifications.models import Notification
from .actions import initpayment, process_response
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .models import DebugMessage
from payments.models import Order, Plan
from users.models import User
from django.conf import settings
import locale
from .serializers import PlanSerializer


TERMINAL_KEY = os.environ.get('TERMINAL_KEY')
TERMINAL_PASSWORD = os.environ.get('TERMINAL_PASSWORD')
SITENAME = settings.SITENAME
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


def subterms(request):
    if request.method == 'GET':
        return render(request, 'payments/sub-terms.html')


class CheckOutView(LoginRequiredMixin, View):
    login_url = '/login/'
    template_name = 'payments/checkout.html'

    def get(self, request):
        data = {
            'sitename': SITENAME,
            'name': request.user.name,
            'email': request.user.email,
            'unread_notifications': Notification.objects.user_unread_count(request.user)}
        expiration_date = datetime.datetime.now() + datetime.timedelta(days=30)
        data['expiration_date'] = expiration_date.strftime('%d %B %Y')
        if request.user.subscriptions.filter(active=True).exists():
            subscription = request.user.subscriptions.get(active=True)
            plan = subscription.plan
            plan_name = plan.name
            data['plans'] = PlanSerializer(
                Plan.objects.filter(price__gte=plan.price), many=True, context={'sub_price': subscription.plan.price, 'date': subscription.expires}
            ).data
        else:
            plan_name = 'Стартер'
            data['plans'] = Plan.objects.all()
        data['plan'] = plan_name
        return render(request, self.template_name, data)

    def post(self, request):
        plan_id = request.POST.get('plan')
        action = request.POST.get('action')
        if action == 'buy':
            user = User.objects.get(email=request.user.email)
            plan = Plan.objects.get(tariff_type=plan_id)
            order = Order.objects.create(user=user, plan=plan, status='NEW')
            out = initpayment(user, plan, order, first_payment=True)
            if out == '1':
                return JsonResponse({
                    'message': out
                })
            return JsonResponse({'url': out['PaymentURL']})
        elif action == 'get_notifications':
            return show_notifications(request)


def pricing(request):
    data = {'sitename': settings.SITENAME,
            'plans': Plan.objects.exclude(tariff_type='0')}
    return render(request, 'payments/pricing.html', data)


@csrf_exempt
def accept_payment(request, *args, **kwargs):
    if request.method == 'POST':
        response = json.loads(request.body)
        try:
            order = Order.objects.get(order_id=response['OrderId'])
            if response['TerminalKey'] == TERMINAL_KEY:
                process_response(response['RebillId'], order, response['Status'])
        except Order.DoesNotExist:
            DebugMessage.objects.create(message='Такого заказа не существует')
        finally:
            return HttpResponse('OK', status=200)
