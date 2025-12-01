from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.core.cache import cache


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, name, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, name, password, **extra_fields)

    def create_superuser(self, email, name, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, name, password, **extra_fields)


class CourseManager(models.Manager):
    def get_all_user_courses(self, user):
        res = cache.get(f'{user.id}_courses')
        if res:
            return res
        else:
            authored_courses = self.filter(author_id=user.id).only('name', 'code')
            student_courses = self.filter(students__id=user.id).only('name', 'code')
            instructor_courses = self.filter(instructors__id=user.id).only('name', 'code')
            all_courses = authored_courses.union(student_courses, instructor_courses)
            cache.set(f'{user.id}_courses', all_courses)
            return all_courses

    def status(self, user, course):
        if user == course.author:
            return '1'
        elif self.filter(id=course.id, students__id=user.id).exists():
            return '0'
        elif self.filter(id=course.id, instructors__id=user.id).exists():
            return '2'
        else:
            return '-1'

    def update_access(self, user):
        try:
            current_limit = user.subscriptions.get(active=True).plan.number_of_unique_students_allowed
        except ObjectDoesNotExist:
            current_limit = 30
        current_number_of_unique_students = user.count_all_unique_students()
        if current_number_of_unique_students > current_limit:
            self.filter(author_id=user.id).update(status='AR')
        else:
            self.filter(author_id=user.id).update(status='PB')

    def get_pinned_threads(self, course):
        return cache.get_or_set(f'cached_pinned_threads_{course.code}', self.threads.selected_related('question').filter(course_id=self.id, is_pinned=True))

    def unenroll(self, course, user):
        status = self.status(user, course)
        if status == '1':
            return '0'
        elif status == '2':
            course.instructors.remove(user)
            cache.delete(f'{user.id}_courses')
            return '1'
        elif status == '0':
            course.students.remove(user)
            cache.delete(f'{user.id}_courses')
            return '1'
        else:
            return '-1'
