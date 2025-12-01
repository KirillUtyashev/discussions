from django.db.models import ForeignKey
from django.utils import timezone
from django.conf import settings
from .helper_functions import calculate_time
from django.db import models
from users.models import User, Course
from .managers import AnswerManager, ThreadManager, WeekManager
from django.core.cache import cache


class AutoDateTimeField(models.DateTimeField):
    def pre_save(self, model_instance, add):
        return timezone.now()


class Viewer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)


class Week(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='weeks', db_index=True)
    from_date = models.DateField()
    to_date = models.DateField()
    objects = WeekManager()

    def __str__(self):
        return f'{self.to_date}-{self.course.name}'

    class Meta:
        indexes = [
            models.Index(fields=["course"]),
        ]
        ordering = ['to_date']


class AbstractCategory(models.Model):
    tag = models.CharField(max_length=50, db_index=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.tag}-{self.id}'


class IntermediateCategory(AbstractCategory):
    pass


class Category(IntermediateCategory):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='categories', db_index=True)


class SubCategory(IntermediateCategory):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subcategories', db_index=True)
    parent_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories', blank=True, null=True)

    def __str__(self):
        return f'subcategory-{self.tag}-{self.course.name}'


class Thread(models.Model):
    type = models.CharField(max_length=50, default='question')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='threads')
    title = models.CharField(max_length=255)
    id_within_course = models.IntegerField()
    category = models.ForeignKey(IntermediateCategory, on_delete=models.CASCADE, related_name='threads')
    views = models.ManyToManyField(Viewer, blank=True)
    is_pinned = models.BooleanField(default=False)
    is_answered = models.BooleanField(default=False)
    question = models.OneToOneField('Question', on_delete=models.CASCADE, related_name='thread')
    week = models.ForeignKey(Week, related_name='threads', on_delete=models.CASCADE)

    objects = ThreadManager()

    class Meta:
        indexes = [
            models.Index(fields=["week", 'course']),
        ]
        ordering = ['question']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            if kwargs['update_fields']:
                cache.delete(f'cached_pinned_threads_{self.course.code}')
                cache.delete(f'cached_regular_threads_{self.course.code}')
        except KeyError:
            if self.is_pinned:
                cache.delete(f'cached_pinned_threads_{self.course.code}')
            else:
                cache.delete(f'cached_regular_threads_{self.course.code}')

    def get_absolute_url(self):
        return self.course.get_absolute_url() + f'?id={self.id}'

    def count_all_answers(self):
        return self.answers.count()

    def count_views(self):
        return self.views.count()

    def add_viewer(self, user):
        if not user:
            self.views.create()
            return
        if not Viewer.objects.filter(user=user).exists():
            Viewer.objects.create(user=user)
        self.views.add(Viewer.objects.get(user=user))

    def week_end(self, category=None):
        if category is None:
            if Thread.objects.get_regular_threads(self.course).filter(week=self.week).first() == self:
                return Week.objects.get_beautiful_date(self.week, self.course)
        else:
            if Thread.objects.get_regular_threads(self.course).filter(category=category, week=self.week).first() == self:
                return Week.objects.get_beautiful_date(self.week, self.course)
            else:
                if type(category) is Category:
                    subcategories = category.subcategories.all()
                    for subcategory in subcategories:
                        if Thread.objects.get_regular_threads(self.course).filter(category=subcategory, week=self.week).first() == self:
                            return Week.objects.get_beautiful_date(self.week, self.course)
            return

    def __str__(self):
        return self.title


class Post(models.Model):
    body = models.TextField()
    is_posted_by_admin = models.BooleanField(default=False)
    created = AutoDateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, blank=True)
    author_name = models.CharField(max_length=50)
    endorsed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='endorsed_posts', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')

    def __str__(self):
        return self.body

    class Meta:
        abstract = True

    def count_all_likes(self):
        return self.likes.count()

    def calculate_time(self):
        return calculate_time(self.created)

    def is_endorsed(self):
        return self.endorsed_by is not None


class IntermediatePost(Post):
    pass


class Question(IntermediatePost):

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.body


class Answer(IntermediatePost):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='answers')

    objects = AnswerManager()

    class Meta:
        ordering = ['-is_posted_by_admin', '-created']

    def __str__(self):
        return self.thread.__str__()


class Comment(IntermediatePost):
    thread = ForeignKey(Thread, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(IntermediatePost, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
