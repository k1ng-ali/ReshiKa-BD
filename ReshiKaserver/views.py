from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, CreateAPIView
from .models import User, Question, Answer
from .serializers import UserSerializer, QuestionSerializer, AnswerSerializer
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import re


@method_decorator(csrf_exempt, name='dispatch')
class RegisterUserView(APIView):
    def post(self, request):
        data = request.data

        # Проверка обязательных полей
        required_fields = ['nickname', 'password', 'repeatPassword']
        if not all(field in data for field in required_fields):
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        # Валидация длины и символов
        if len(data['nickname']) < 6 or len(data['nickname']) > 15:
            return Response({"error": "Nickname must be between 6 and 15 characters"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not re.match(r'^[a-zA-Z0-9-]+$', data['nickname']):
            return Response({"error": "Nickname can only contain letters, numbers and hyphens"},
                            status=status.HTTP_400_BAD_REQUEST)

        if data['password'] != data['repeatPassword']:
            return Response({"error": "Passwords don't match"},
                            status=status.HTTP_400_BAD_REQUEST)

        if len(data['password']) < 6:
            return Response({"error": "Password must be at least 6 characters"},
                            status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(nickname=data['nickname']).exists():
            return Response({"error": "Nickname already exists"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Подготовка данных для сохранения
        user_data = {
            'nickname': data['nickname'],
            'password': data['password'],
            'first_name': data.get('firstName'),
            'last_name': data.get('lastName'),
            'email': data.get('email')
        }

        serializer = UserSerializer(data=user_data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User registered successfully",
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class LoginUserView(APIView):
    def post(self, request):
        data = request.data
        if 'nickname' not in data or 'password' not in data:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(nickname=data['nickname'])
        except User.DoesNotExist:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)

        if not check_password(data['password'], user.password):
            return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": "Login successful",
            "user": {
                "nickname": user.nickname,
                "firstName": user.first_name,
                "lastName": user.last_name
            }
        }, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class QuestionListCreateView(ListCreateAPIView):
    queryset = Question.objects.all().order_by('-created_at')
    serializer_class = QuestionSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(author=user)

@method_decorator(csrf_exempt, name='dispatch')
class QuestionDetailView(RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

@method_decorator(csrf_exempt, name='dispatch')
class AnswerCreateView(CreateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    def perform_create(self, serializer):
        user = self.request.user
        question_id = self.request.data.get('question_id')
        reply_to_id = self.request.data.get('reply_to_id')
        reply_to_answer_id = self.request.data.get('reply_to_answer_id')

        question = Question.objects.get(id=question_id)
        reply_to = User.objects.get(id=reply_to_id) if reply_to_id else None
        reply_to_answer = Answer.objects.get(id=reply_to_answer_id) if reply_to_answer_id else None

        answer = serializer.save(author=user, reply_to=reply_to, reply_to_answer=reply_to_answer)
        question.answers.add(answer)