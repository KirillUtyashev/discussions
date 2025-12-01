import datetime
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils import timezone
from .managers import CourseManager, UserManager
from django.core.validators import MinLengthValidator


def closest_sunday(today):
    """
    Returns the date of the next given weekday after
    the given date. For example, the date of next Monday.

    NB: if it IS the day we're looking for, this returns 0.
    consider then doing onDay(foo, day + 1).
    """
    sunday = today + datetime.timedelta((6-today.weekday()) % 7)
    res = sunday.date()
    return res


class AutoDateTimeField(models.DateTimeField):
    def pre_save(self, model_instance, add):
        return timezone.now()


class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True, db_index=True)
    password = models.CharField(max_length=255)
    username = None
    email_is_verified = models.BooleanField(default=False)
    avatar = models.ImageField(default='profile.svg', upload_to='img')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', ]

    class Meta:
        app_label = 'users'

    def __str__(self):
        return self.email

    def change_name(self, new_name):
        self.name = new_name
        self.save()

    def get_created_courses(self):
        created_courses = self.courses_created.all()
        if created_courses:
            return created_courses

    def count_all_unique_students(self):
        courses_managed = self.get_created_courses()
        if courses_managed:
            unique_students = None
            for course in courses_managed:
                if unique_students:
                    unique_students = unique_students.union(unique_students, User.objects.filter(courses_joined__id=course.id))
                else:
                    unique_students = User.objects.filter(courses_joined__id=course.id)
            return len(unique_students)
        return 0


class Course(models.Model):

    class Status(models.TextChoices):
        PUBLISHED = 'PB', 'PUBLISHED'
        ARCHIVED = 'AR', 'ARCHIVED'

    name = models.CharField(max_length=255)
    code = models.SlugField(validators=[MinLengthValidator(4)], max_length=7, unique=True, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_created')
    students = models.ManyToManyField(User, related_name='courses_joined')
    instructors = models.ManyToManyField(User, related_name='courses_instructed')
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.PUBLISHED)
    password = models.CharField(max_length=255, blank=True, null=True)
    is_demo = models.BooleanField(default=False)
    created = AutoDateTimeField(default=timezone.now)
    is_active_link = models.BooleanField(default=True)

    objects = CourseManager()

    class Meta:
        indexes = [
            models.Index(fields=["code"]),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.weeks.exists():
            self.create_first_week()
        if not self.categories.all():
            self.categories.create(tag='Общее')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('discussionboard:course', kwargs={'course_slug': self.code})

    def get_thread_id(self):
        return self.threads.all().count() + 1

    def create_new_week(self):
        return self.weeks.create(from_date=timezone.now(), to_date=timezone.now() + timedelta(days=7), course_id=self.id)

    def create_first_week(self):
        from_date = self.created
        to_date = closest_sunday(from_date)
        return self.weeks.create(from_date=from_date, to_date=to_date, course_id=self.id)

    def get_threads(self):
        return self.threads.all()

    def get_ids_of_admins(self):
        res = [self.author.id]
        for instructor in self.instructors.all():
            res.append(instructor.pk)
        return res

    def get_invite_link(self):
        domain = 'discussions.ru'
        path = reverse('discussionboard:join-course', kwargs={'course_slug': self.code})
        url = f'https://{domain}{path}'
        return url

    def get_settings_url(self):
        return reverse('discussionboard:settings', kwargs={'course_slug': self.code})

    def verify_access(self):
        return self.status == 'PB'

