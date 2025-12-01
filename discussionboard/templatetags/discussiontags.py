from django import template
from discussionboard.models import IntermediatePost

register = template.Library()


@register.simple_tag(takes_context=True)
def is_liked_by_user(context, obj):
    if isinstance(obj, str):
        return
    user = context['request'].user
    if user.is_anonymous:
        return False
    return IntermediatePost.objects.filter(id=obj.id, likes=user).exists()
