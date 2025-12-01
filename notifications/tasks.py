from discussionboard.models import Thread
from notifications.models import Notification
from DilemmaPlatform.celery import app
from users.models import Course


@app.task
def send_post_email(course_id, thread_id):
    course = Course.objects.get(id=course_id)
    thread = Thread.objects.get(id=thread_id)
    message = f'<b>{thread.question.author.name}</b> выложил(а) объявление: {thread.title}'
    users = course.students.filter(email_is_verified=True).only('email')
    Notification.objects.notify_class(users=users, message=message, thread=thread)


@app.task
def notify_user(user_id, message, thread_id):
    Notification.objects.notify_user(user_id=user_id, message=message, thread_id=thread_id)
