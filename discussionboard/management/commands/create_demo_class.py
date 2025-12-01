import datetime

from django.core.management.base import BaseCommand

from discussionboard.actions import post_thread
from users.models import User, Course
from discussionboard.models import Question, Thread, Answer, Comment
from dateutil.relativedelta import relativedelta


class Command(BaseCommand):
    help = 'Создает базовые планы'

    def handle(self, *args, **kwargs):
        if Course.objects.filter(is_demo=True).exists():
            course = Course.objects.filter(is_demo=True)
            User.objects.filter(courses_joined=course[0]).delete()
            User.objects.filter(courses_instructed=course[0]).delete()
            course.delete()
        # Создаем курс
        author = User.objects.get(is_superuser=True)
        course = Course.objects.create(name='Дискретная математика', code='democls', author=author, is_demo=True)
        # Создаем учеников + 1 инструктора
        instructor = User.objects.create(name='Виктор Андреев', email='viktor@mail.com', password='12345678')
        course.instructors.add(instructor)
        dmitry = User.objects.create(name='Дмитрий', email='dmitriy@mail.com', password='12345678')
        ilya = User.objects.create(name='Илья Колесников', email='ilya@mail.com', password='12345678')
        anna = User.objects.create(name='Анна Власова', email='anna@mail.com', password='12345678')
        liza = User.objects.create(name='Лиза', email='liza@mail.com', password='12345678')
        students = [dmitry, ilya, anna, liza]
        for student in students:
            course.students.add(student)
        # Создаем категории
        general = course.categories.first()
        course.categories.create(tag='Лекции')
        course.categories.create(tag='Тесты')
        course.categories.create(tag='Рабочие листы')
        course.categories.create(tag='Задачи')
        body = '''<p>Всем привет!</p>
        <p>Мы будем использовать Дискуссии.ру для того, чтобы задавать вопросы по содержанию или административным аспектам курса. Здесь вы получите быстрые ответы от преподавателей и однокурсников и удобный поиск уже существующих вопросов.</p>
        <p>Вот несколько советов:</p>
        <ul>
        <li>Пожалуйста, ищите, прежде чем задавать вопрос - возможно на него уже есть ответ!&nbsp;</li>
        <li>Грамотно выберайте подходящую категорию для новых вопросов.</li>
        <li>Публикуйте вопросы и ответы, которые вы считаете полезными, - это поможет всем быстрее находить полезный контент.</li>
        <li>Отвечайте на вопросы, на которые вы чувствуете себя уверенно, но даже если вы не уверены, не стесняйтесь: мы все учимся большему, обмениваясь идеями!</li>
        </ul>
        <p>Мы с нетерпением ждем начала учебного года!</p>
        <p>Лев Павлович</p>'''
        post_thread(user=author, header='Добро пожаловать!', body=body, cat=general.id, name="Лев Павлович", post_type='post', course=course)
