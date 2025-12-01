from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from .models import Comment, IntermediatePost, SubCategory, Thread, Question, \
    Answer, \
    Category, Week
from users.serializers import UserSerializer, CourseSerializer


# Post-related serializers

class PostSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=50)
    all_likes = serializers.IntegerField(source='count_all_likes')
    time = serializers.CharField(source='calculate_time')
    is_liked_by_user = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    is_endorsed = serializers.BooleanField()

    def get_is_endorsed(self, obj):
        return

    def get_is_author(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.email == obj.author.email
        return False

    def get_is_liked_by_user(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.likes.filter(
            email=user.email
        ).exists()

    class Meta:
        fields = ['all_likes', 'time', 'is_liked_by_user',
                  'id', 'body', 'is_author', 'is_posted_by_admin', 'is_endorsed']


class CommentSerializer(PostSerializer, serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()

    def get_comments(self, obj):
        if obj.comments is not None:
            return CommentSerializer(obj.comments, many=True, context=self.context).data

    class Meta:
        model = Comment
        fields = PostSerializer.Meta.fields + ['author_name', 'comments']


class IntermediateSerializer(PostSerializer, serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = IntermediatePost
        fields = PostSerializer.Meta.fields + ['comments']


class AnswerSerializer(IntermediateSerializer, serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = IntermediateSerializer.Meta.fields + ['author_name']


class ShortQuestionSerializer(IntermediateSerializer, serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['author_name', 'time', 'all_likes', 'is_liked_by_user',
                  'all_likes', 'id']


class SearchQuestionSerializer(IntermediateSerializer, serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['author_name', 'time', 'body']


class QuestionSerializer(IntermediateSerializer, serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = IntermediateSerializer.Meta.fields + ['author_name']


# Category-related serializers

class AbstractCategorySerializer(serializers.Serializer):
    tag = serializers.CharField(max_length=50)

    class Meta:
        fields = ['tag', 'id']


class SubCategorySerializer(AbstractCategorySerializer, serializers.ModelSerializer):

    class Meta:
        model = SubCategory
        fields = AbstractCategorySerializer.Meta.fields


class CategorySerializer(AbstractCategorySerializer, serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = AbstractCategorySerializer.Meta.fields + ['subcategories']


# Thread-related serializers

class ThreadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    all_answers = serializers.IntegerField(source='count_all_answers')
    views = serializers.IntegerField(source='count_views')

    class Meta:
        model = Thread
        fields = ['id', 'category', 'views', 'all_answers',
                  'is_pinned', 'type',
                  'views', 'title']


# Use this serializer when function get_thread is called
class FullThreadSerializer(ThreadSerializer):
    answers = AnswerSerializer(read_only=True, many=True)
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = Thread
        fields = ThreadSerializer.Meta.fields + ['answers', 'question']


# Use this serializer when you need to serialize pinned threads when filtering
class PinnedThreadSerializer(ThreadSerializer):
    question = ShortQuestionSerializer(read_only=True)

    class Meta:
        model = Thread
        fields = ThreadSerializer.Meta.fields + ['question', 'is_answered']


# Use this serializer to serialize regular threads when filtering
class RegularThreadSerializer(PinnedThreadSerializer):
    week_end = serializers.SerializerMethodField()

    def get_week_end(self, obj):
        category = self.context.get('category')
        return obj.week_end(category)

    class Meta:
        model = Thread
        fields = PinnedThreadSerializer.Meta.fields + ['week_end']


# Use this serializer to serialize threads appearing in search
class SearchThreadSerializer(ThreadSerializer):
    question = SearchQuestionSerializer(read_only=True)

    class Meta:
        model = Thread
        fields = ['id', 'title', 'question', 'category']
