import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.cache import cache

from discussionboard.actions import post_thread
from users.actions import generate_unique_code
from users.models import Course, User
from discussionboard.models import Category, Comment, Question, SubCategory, Week
from payments.models import Subscription


class Command(BaseCommand):
    help = 'Чистит бд'

    def handle(self, *args, **kwargs):
        cache.clear()
        User.objects.filter(is_superuser=False).delete()
        Course.objects.filter(is_demo=False).delete()
        names = ['Nika', 'Kirill', 'Marat', 'Egor', 'Tim']
        courses = ['MAT135', 'ECO102', 'STA130']
        # Создание юзеро
        for name in names:
            user = User.objects.create_user(email=f'{name.lower()}@mail.com', name=name, password='123456')
            user.subscriptions.create(plan_id='1', expires=timezone.now() + datetime.timedelta(days=30), renewal=True)
        # Создание курсов с создателем Nika и инструктором Tim
        for course in courses:
            course = Course.objects.create(name=course, code=generate_unique_code(), author=User.objects.get(email='nika@mail.com'))
            course.instructors.add(User.objects.get(email='tim@mail.com'))
            course.categories.create(tag='Семинары')
        # Создание вопросов
        nika = User.objects.get(email='nika@mail.com')
        user_questions = User.objects.get(email='egor@mail.com')
        course = Course.objects.get(name='MAT135')
        for student in User.objects.exclude(email__in=['nika@mail.com', 'tim@mail.com']):
            student.courses_joined.add(course)
        Category.objects.create(tag='Лекции', course_id=course.id)
        cat_1 = Category.objects.get(tag='Лекции', course_id=course.id)
        cat_1.subcategories.add(SubCategory.objects.create(tag='Лекция 1', course_id=course.id))
        subcat_1 = SubCategory.objects.get(tag='Лекция 1')
        cat_1.subcategories.add(SubCategory.objects.create(tag='Лекция 2', course_id=course.id))
        course.categories.add(cat_1)
        domashki = course.categories.create(tag='Домашки')
        week_before = Week.objects.create(from_date=datetime.datetime(2024, 7, 28, 23, 59, 0), to_date=datetime.datetime(2024, 7, 21, 23, 59, 0), course_id=course.id)
        week_before_before = Week.objects.create(from_date=datetime.datetime(2024, 7, 21, 23, 59, 0), to_date=datetime.datetime(2024, 7, 14, 23, 59, 0), course_id=course.id)
        current_week = course.weeks.last()
        for i in range(3):
            post_thread(nika, 'Объявление 1', f'Это текст объявления номер {i}', cat_1.id, nika.name, 'post', course)
        for i in range(2):
            thread_id = course.threads.all().count()
            question = Question.objects.create(body=f'Это текст вопроса номер {i}', author_id=user_questions.id, author_name=user_questions.name)
            a = course.threads.create(title=f'Вопрос 1', category=cat_1, course=course, id_within_course=thread_id, question_id=question.id, week=week_before_before, is_pinned=True)
            comment = Comment.objects.create(body='Коммент', author_id=user_questions.id, post_id=question.id, author_name=user_questions.name, thread_id=a.id)
            a.comments.create(body='Коммент 2', author_id=user_questions.id, post_id=comment.id, author_name=user_questions.name, thread_id=a.id)
            a.answers.create(author_id=user_questions.id, body='Ответ 1', author_name=user_questions.name, thread_id=a.id)
        for i in range(2):
            thread_id = course.threads.all().count()
            question = Question.objects.create(body=f'Это текст вопроса номер {i}', author_id=user_questions.id, author_name=user_questions.name)
            a = course.threads.create(title=f'Вопрос 2', category=cat_1, course=course, id_within_course=thread_id, question_id=question.id, week=week_before, is_pinned=True)
            comment = Comment.objects.create(body='Коммент', author_id=user_questions.id, post_id=question.id, author_name=user_questions.name, thread_id=a.id)
            a.comments.create(body='Коммент 2', author_id=user_questions.id, post_id=comment.id, author_name=user_questions.name, thread_id=a.id)
            a.answers.create(author_id=user_questions.id, body='Ответ 1', author_name=user_questions.name, thread_id=a.id)
        for i in range(2):
            thread_id = course.threads.all().count()
            question = Question.objects.create(body=f'Это текст вопроса номер {i}', author_id=user_questions.id, author_name=user_questions.name)
            a = course.threads.create(title=f'Вопрос 3', category=cat_1, course=course, id_within_course=thread_id, question_id=question.id, week=current_week, is_pinned=True)
            comment = Comment.objects.create(body='Коммент', author_id=user_questions.id, post_id=question.id, author_name=user_questions.name, thread_id=a.id)
            a.comments.create(body='Коммент 2', author_id=user_questions.id, post_id=comment.id, author_name=user_questions.name, thread_id=a.id)
            a.answers.create(author_id=user_questions.id, body='Ответ 1', author_name=user_questions.name, thread_id=a.id)
        for i in range(2):
            thread_id = course.threads.all().count()
            question = Question.objects.create(body=f'Это текст вопроса номер {i}', author_id=user_questions.id, author_name=user_questions.name)
            a = course.threads.create(title=f'Задача 1', category=domashki, course=course, id_within_course=thread_id, question_id=question.id, week=week_before_before)
            comment = Comment.objects.create(body='Коммент', author_id=user_questions.id, post_id=question.id, author_name=user_questions.name, thread_id=a.id)
            a.comments.create(body='Коммент 2', author_id=user_questions.id, post_id=comment.id, author_name=user_questions.name, thread_id=a.id)
            a.answers.create(author_id=user_questions.id, body='Ответ 1', author_name=user_questions.name, thread_id=a.id)
        for i in range(2):
            thread_id = course.threads.all().count()
            question = Question.objects.create(body=f'Это текст вопроса номер {i}', author_id=user_questions.id, author_name=user_questions.name)
            a = course.threads.create(title=f'Задача 2', category=cat_1, course=course, id_within_course=thread_id, question_id=question.id, week=week_before_before)
            comment = Comment.objects.create(body='Коммент', author_id=user_questions.id, post_id=question.id, author_name=user_questions.name, thread_id=a.id)
            a.comments.create(body='Коммент 2', author_id=user_questions.id, post_id=comment.id, author_name=user_questions.name, thread_id=a.id)
            a.answers.create(author_id=user_questions.id, body='Ответ 1', author_name=user_questions.name, thread_id=a.id)
        for i in range(2):
            thread_id = course.threads.all().count()
            question = Question.objects.create(body=f'Это текст вопроса номер {i}', author_id=user_questions.id, author_name=user_questions.name)
            a = course.threads.create(title=f'Задача 3', category=subcat_1, course=course, id_within_course=thread_id, question_id=question.id, week=week_before)
            comment = Comment.objects.create(body='Коммент', author_id=user_questions.id, post_id=question.id, author_name=user_questions.name, thread_id=a.id)
            a.comments.create(body='Коммент 2', author_id=user_questions.id, post_id=comment.id, author_name=user_questions.name, thread_id=a.id)
            a.answers.create(author_id=user_questions.id, body='Ответ 1', author_name=user_questions.name, thread_id=a.id)
        for i in range(2):
            thread_id = course.threads.all().count()
            question = Question.objects.create(body=f'Это текст вопроса номер {i}', author_id=user_questions.id, author_name=user_questions.name)
            a = course.threads.create(title=f'Задача 4', category=domashki, course=course, id_within_course=thread_id, question_id=question.id, week=week_before)
            comment = Comment.objects.create(body='Коммент', author_id=user_questions.id, post_id=question.id, author_name=user_questions.name, thread_id=a.id)
            a.comments.create(body='Коммент 2', author_id=user_questions.id, post_id=comment.id, author_name=user_questions.name, thread_id=a.id)
            a.answers.create(author_id=user_questions.id, body='Ответ 1', author_name=user_questions.name, thread_id=a.id)
        for i in range(2):
            thread_id = course.threads.all().count()
            question = Question.objects.create(body=f'Это текст вопроса номер {i}', author_id=user_questions.id, author_name=user_questions.name)
            a = course.threads.create(title=f'Задача 5', category=cat_1, course=course, id_within_course=thread_id, question_id=question.id, week=current_week)
            comment = Comment.objects.create(body='Коммент', author_id=user_questions.id, post_id=question.id, author_name=user_questions.name, thread_id=a.id)
            a.comments.create(body='Коммент 2', author_id=user_questions.id, post_id=comment.id, author_name=user_questions.name, thread_id=a.id)
            a.answers.create(author_id=user_questions.id, body='Ответ 1', author_name=user_questions.name, thread_id=a.id)
        for i in range(2):
            thread_id = course.threads.all().count()
            question = Question.objects.create(body=f'Это текст вопроса номер {i}', author_id=user_questions.id, author_name=user_questions.name)
            a = course.threads.create(title=f'Задача 6', category=domashki, course=course, id_within_course=thread_id, question_id=question.id, week=current_week)
            comment = Comment.objects.create(body='Коммент', author_id=user_questions.id, post_id=question.id, author_name=user_questions.name, thread_id=a.id)
            a.comments.create(body='Коммент 2', author_id=user_questions.id, post_id=comment.id, author_name=user_questions.name, thread_id=a.id)
            a.answers.create(author_id=user_questions.id, body='Ответ 1', author_name=user_questions.name, thread_id=a.id)
