from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Question, Answer, Comment, Thread
from django.core.cache import cache


@receiver(post_delete, sender=Thread)
def clear_cache(sender, instance, **kwargs):
    if instance.is_pinned:
        cache.delete(f'cached_pinned_threads_{instance.course.code}')
    else:
        cache.delete(f'cached_regular_threads_{instance.course.code}')


@receiver(post_save, sender=Answer)
def update_is_posted_by_admin_answer(sender, instance, created, **kwargs):
    if created:
        update_thread_answered(instance)


@receiver(post_save, sender=Comment)
def update_is_posted_by_admin_comment(sender, instance, created, **kwargs):
    if created:
        update_thread_answered(instance)


def update_thread_answered(post: Answer | Comment) -> None:
    if post.author.id in post.thread.course.get_ids_of_admins():
        post.is_posted_by_admin = True
        post.save(update_fields=['is_posted_by_admin'])


