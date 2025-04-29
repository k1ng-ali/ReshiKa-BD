from rest_framework import serializers
from .models import User, Question, Answer
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nickname', 'password', 'first_name', 'last_name', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class AnswerSerializer(serializers.ModelSerializer):
    author_nickname = serializers.CharField(source='author.nickname', read_only=True)
    reply_to_nickname = serializers.CharField(source='reply_to.nickname', read_only=True, allow_null=True)

    class Meta:
        model = Answer
        fields = ['id', 'content', 'likes', 'author_nickname', 'created_at', 'reply_to_nickname', 'reply_to_answer']

class QuestionSerializer(serializers.ModelSerializer):
    author_nickname = serializers.CharField(source='author.nickname', read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'title', 'content', 'likes', 'author_nickname', 'created_at', 'answers']