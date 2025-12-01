from .base import *

DEBUG = False

ALLOWED_HOSTS = ['discussions.ru', 'www.discussions.ru', '95.163.223.133']
CSRF_TRUSTED_ORIGINS = ['http://discussions.ru', 'https://discussions.ru']
STATIC_ROOT = "/var/www/dilemmapp/static/"
