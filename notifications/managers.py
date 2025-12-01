from django.db import models
from utils.send_user_email import send_user_email
from discussionboard.models import Thread
from users.models import User
from django.core.cache import cache
from bs4 import BeautifulSoup


class NotificationQuerySet(models.QuerySet):
    """Custom QuerySet for Notification model"""

    def update(self, *args, **kwargs):
        """Override update to ensure cache is invalidated on very call."""
        super().update(**kwargs)
        user_pks = set(self.select_related("user").values_list('user__pk', flat=True))
        for user_pk in user_pks:
            cache.delete(f"notifications_{user_pk}")


class NotificationManager(models.Manager):
    email_template_name = 'notifications/notification.html'
    NOTIFICATIONS_MAX_PER_USER = 20
    USER_NOTIFICATION_COUNT_CACHE_DURATION = 86_400

    def get_queryset(self):
        return NotificationQuerySet(self.model, using=self._db)

    def notify_user(self, user_id: str, message: str, thread_id: str) -> object:
        """
        Отправка уведомления пользователю. Функция возвращает новое уведомление.
        """
        user = User.objects.get(pk=user_id)
        if not user.email_is_verified:
            return
        thread = Thread.objects.get(pk=thread_id)
        self._remove_redundant_notifications(user)
        obj = self.create(user=user, message=message, thread=thread)
        cache.delete(f"notifications_{user_id}")
        # Sending email
        subject = f'Новый ответ в классе {thread.course.name}'
        email_template_name = self.email_template_name
        parameters = {
            'message': BeautifulSoup(message, features="html.parser").get_text(),
            'link': 'https://discussions.ru/' + f'{thread.get_absolute_url()}'
        }
        send_user_email(subject, email_template_name, [user.email], parameters)
        return obj

    def user_unread_count(self, user) -> int:
        """Возвращает количество непросмотренных уведомлений.
        """
        unread_count = cache.get_or_set(
            key=f'notifications_{user.id}',
            default=self.filter(user__id=user.id, viewed=False).count(),
            timeout=self.USER_NOTIFICATION_COUNT_CACHE_DURATION)
        return unread_count

    def _remove_redundant_notifications(self, user):
        max_notifications = self.NOTIFICATIONS_MAX_PER_USER
        if self.filter(user=user).count() >= max_notifications:
            to_be_deleted_qs = self.filter(user=user).order_by(
                "-created"
            )[max_notifications - 1:]
            for notification in to_be_deleted_qs:
                notification.delete()
            cache.delete(f"notifications_{user.pk}")

    def notify_class(self, users, message: str, thread) -> None:
        for user in users:
            self._remove_redundant_notifications(user)
            self.create(user=user, message=message, thread=thread)
            cache.delete(f"notifications_{user.id}")
        subject = f'Новое объявление в классе {thread.course.name}'
        email_template_name = self.email_template_name
        parameters = {
            'message': BeautifulSoup(message, features="html.parser").get_text(),
            'link': 'https://discussions.ru/' + f'{thread.get_absolute_url()}'
        }
        send_user_email(subject, email_template_name, [user.email for user in users], parameters)

