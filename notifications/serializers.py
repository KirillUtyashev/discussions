from rest_framework import serializers
from .models import Notification
from discussionboard.helper_functions import calculate_time


class NotificationSerializer(serializers.ModelSerializer):
    thread_url = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()

    def get_thread_url(self, obj):
        return obj.thread.get_absolute_url()

    def get_time(self, obj):
        return calculate_time(obj.created)

    def get_course(self, obj):
        return obj.thread.course.name

    class Meta:
        model = Notification
        fields = ['message', 'time', 'thread_url', 'course', 'viewed']
