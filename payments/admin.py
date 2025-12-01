from django.contrib import admin

from payments.models import Order, Plan, Subscription, DebugMessage

admin.site.register(Order)
admin.site.register(Plan)
admin.site.register(Subscription)
admin.site.register(DebugMessage)
