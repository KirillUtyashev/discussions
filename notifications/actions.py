from django.http import JsonResponse

from notifications.models import Notification
from notifications.serializers import NotificationSerializer


def show_notifications(request):
    user = request.user
    notifications = Notification.objects.filter(user=user)
    return JsonResponse({
        'notifications': NotificationSerializer(notifications, many=True).data
    })
