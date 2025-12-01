from django.urls import path

from payments.views import CheckOutView, accept_payment, pricing, subterms

app_name = 'payments'

urlpatterns = [
    path('checkout/', CheckOutView.as_view(), name='checkout'),
    path('pricing/', pricing, name='pricing'),
    path('payment/', accept_payment, name='accept-payment'),
    path('sub-terms/', subterms, name='subterms')
    ]
