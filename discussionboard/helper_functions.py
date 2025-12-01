from django.http import JsonResponse
from django.utils import timezone

from users.models import Course, User

# Functions used in models.py
SECONDS_MINUTES_MATCH = {
    1: 'у',
    2: 'ы',
    3: 'ы',
    4: 'ы',
    5: '',
    6: '',
    7: '',
    8: '',
    9: '',
    0: '',
}


HOURS_MATCH = {
    1: '',
    2: 'а',
    3: 'а',
    4: 'а',
    5: 'ов',
    6: 'ов',
    7: 'ов',
    8: 'ов',
    9: 'ов',
    0: 'ов'
}

MONTHS_MATCH = {
    1: '',
    2: 'а',
    3: 'а',
    4: 'а',
    5: 'ев',
    6: 'ев',
    7: 'ев',
    8: 'ев',
    9: 'ев',
    0: 'ев'
}

DAYS_MATCH = {
    1: 'день',
    2: 'дня',
    3: 'дня',
    4: 'дня',
    5: 'дней',
    6: 'дней',
    7: 'дней',
    8: 'дней',
    9: 'дней',
    0: 'дней',
}


YEARS_MATCH = {
    1: 'год',
    2: 'года',
    3: 'года',
    4: 'года',
    5: 'лет',
    6: 'лет',
    7: 'лет',
    8: 'лет',
    9: 'лет',
    0: 'лет'
}


def find_ending(time: int, time_format: str) -> str:
    if time_format == 'seconds' or time_format == 'minutes':
        dictionary = SECONDS_MINUTES_MATCH
    elif time_format == 'hours':
        dictionary = HOURS_MATCH
    elif time_format == 'days':
        dictionary = DAYS_MATCH
    elif time_format == 'months':
        dictionary = MONTHS_MATCH
    else:
        dictionary = YEARS_MATCH
    if time < 10:
        ending = dictionary[time]
    elif 10 <= time < 20:
        if time_format == 'seconds' or time_format == 'minutes':
            ending = ''
        elif time_format == 'hours':
            ending = 'ов'
        elif time_format == 'days':
            ending = 'дней'
        elif time_format == 'months':
            ending = 'ев'
        else:
            ending = 'лет'
    else:
        last_int = str(time)[-1]
        ending = dictionary[int(last_int)]
    return ending


def calculate_time(created: timezone) -> str:
    time = int((timezone.now() - created).total_seconds())
    minutes = time // 60
    hours = minutes // 60
    days = hours // 24
    months = days // 30
    years = months // 12
    if time <= 1:
        return 'Только что'
    elif time < 60:
        ending = find_ending(time, 'seconds')
        return f'{time} секунд{ending} назад'
    elif minutes < 60:
        ending = find_ending(minutes, 'minutes')
        return f'{minutes} минут{ending} назад'
    elif hours < 24:
        ending = find_ending(hours, 'hours')
        return f'{hours} час{ending} назад'
    elif days < 30:
        ending = find_ending(days, 'days')
        return f'{days} {ending} назад'
    elif months < 12:
        ending = find_ending(months, 'months')
        return f'{months} месяц{ending} назад'
    else:
        ending = find_ending(years, 'years')
        return f'{years} {ending} назад'


# Functions used in views.py
def negative_response() -> JsonResponse:
    return JsonResponse({
        'message': '-1'
    })


def check_status(user, course) -> str:
    """
    1 - student
    0 - admin
    -1 - restricted
    """
    if User.objects.filter(id=user.id, courses_joined__id=course.id).exists():
    # if course.students.filter(id=user.id).exists():
        return '1'
    # elif (course.instructors.filter(id=user.id).exists() or
    #       course.author == user):
    elif (User.objects.filter(id=user.id, courses_instructed__id=course.id).exists() or
          User.objects.filter(id=user.id, courses_created__id=course.id)):
        return '0'
    else:
        return '-1'
