from django import template

from users.models import User

register = template.Library()


@register.simple_tag(takes_context=True)
def is_admin(context, obj):
    user = context['request'].user
    if (User.objects.filter(id=user.id, courses_instructed__id=obj.id).exists() or
            User.objects.filter(id=user.id, courses_created__id=obj.id).exists()):
        return '1'
    return '0'
