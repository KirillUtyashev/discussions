from rest_framework import serializers
from .models import Plan, Subscription


class PlanSerializer(serializers.ModelSerializer):
    price_to_pay = serializers.SerializerMethodField()
    price_rubles = serializers.CharField()

    def get_price_to_pay(self, obj):
        price = self.context.get('sub_price')
        date = self.context.get('date')
        if obj.price == price:
            return
        return obj.calculate_price_to_pay(date, price) / 100

    class Meta:
        model = Plan
        fields = ['tariff_type', 'name', 'for_whom', 'number_of_unique_students_allowed',
                  'price_to_pay', 'price_rubles']
