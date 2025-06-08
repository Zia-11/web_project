from django.shortcuts import render
from django.contrib.auth import get_user_model, authenticate, login, logout
from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response


# Create your views here.

User = get_user_model()

# регистрация (доступна всем)
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

# список пользователей (требует аутентификации)
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user = authenticate(
            request,
            username=request.data.get('username'),
            password=request.data.get('password'),
        )
        if not user:
            return Response({'detail': 'Неверные учётные данные'},
                            status=status.HTTP_400_BAD_REQUEST)
        login(request, user)
        return Response({'detail': 'Успешно залогинены'})

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)