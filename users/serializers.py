from rest_framework import serializers

from users.models import User, Course


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'avatar']


class CourseSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()
    settings_url = serializers.CharField(source='get_settings_url', read_only=True)

    def get_is_admin(self, obj):
        user = self.context.get('request').user
        if (obj.instructors.filter(email=user.email).exists() or
                obj.author.email == user.email):
            return '1'
        return '0'

    class Meta:
        model = Course
        fields = ['name', 'is_admin', 'code', 'settings_url']
