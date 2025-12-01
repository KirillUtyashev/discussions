import datetime
from django.core.cache import cache
from django.db import models

MONTHS_DICT = {
    '01': 'января',
    '02': 'февраля',
    '03': 'марта',
    '04': 'апреля',
    '05': 'мая',
    '06': 'июня',
    '07': 'июля',
    '08': 'августа',
    '09': 'сентября',
    '10': 'октября',
    '11': 'ноября',
    '12': 'декабря'
}


class WeekManager(models.Manager):

    def get_beautiful_date(self, week, course):
        if week == self.filter(course=course).last() and datetime.date.today() <= week.to_date:
            return 'Текущая неделя'
        day = week.to_date.strftime('%d')
        month = week.to_date.strftime('%m')
        time_difference = datetime.date.today() - week.to_date
        if time_difference.days >= 30:
            year = week.to_date.strftime('%Y')
            result = f'{day} {MONTHS_DICT[month]}, {year}'
        else:
            result = f'{day} {MONTHS_DICT[month]}'
        return result


class ThreadManager(models.Manager):

    def create(self, **kwargs):
        thread = super().create(**kwargs)
        if thread.question.author.id in thread.course.get_ids_of_admins():
            thread.question.is_posted_by_admin = True
            thread.question.save(update_fields=['is_posted_by_admin'])
        return thread

    def get_pinned_threads(self, course):
        return cache.get_or_set(f'cached_pinned_threads_{course.code}', self.select_related('question', 'category').filter(course=course, is_pinned=True))

    def get_regular_threads(self, course):
        return cache.get_or_set(f'cached_regular_threads_{course.code}', self.select_related('question', 'category').filter(course=course, is_pinned=False))


class AnswerQuerySet(models.QuerySet):
    def update(self, **kwargs):
        super().update(**kwargs)
        thread = self[0].thread
        if kwargs['endorsed_by']:
            thread.is_answered = True
        else:
            thread.is_answered = False
        thread.save(update_fields=['is_answered'])

    def delete(self, **kwargs):
        if len(self) == 0:
            return super().delete()
        ans = self[0]
        if ans.thread.is_answered and (ans.endorsed_by or ans.author.id in ans.thread.course.get_ids_of_admins()):
            ans.thread.is_answered = False
            ans.thread.save(update_fields=['is_answered'])
        return super().delete()


class AnswerManager(models.Manager):
    def create(self, **kwargs):
        ans = super().create(**kwargs)
        thread = ans.thread
        if not thread.is_answered and ans.author.id in thread.course.get_ids_of_admins():
            thread.is_answered = True
            thread.save(update_fields=['is_answered'])
        return ans

    def get_queryset(self):
        return AnswerQuerySet(self.model, using=self._db)

