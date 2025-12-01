from DilemmaPlatform.celery import app
from users.models import User
from utils.send_user_email import send_user_email


@app.task
def new_subscription_email(user_id, plan_name, template):
    user = User.objects.get(id=user_id)
    subject = f'Успешное оформление подписки'
    parameters = {
        'message': f'Ваш текущий план: {plan_name}'
    }
    send_user_email(subject, template, [user.email], parameters)
