from django.db import models

from notifications.managers import NotificationManager
from users.models import User
from discussionboard.models import Thread
from discussionboard.models import AutoDateTimeField
from django.utils import timezone


class Notification(models.Model):
    """
    Уведомление пользователям.
    """

    message = models.TextField()
    created = AutoDateTimeField(default=timezone.now)
    viewed = models.BooleanField(default=False, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='notifications')
    objects = NotificationManager()

    def __str__(self) -> str:
        return f"{self.user}: {self.message}"

    class Meta:
        indexes = [
            models.Index(fields=['user', 'thread']),
        ]
        ordering = ['-created']

