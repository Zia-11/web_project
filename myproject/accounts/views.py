from django.shortcuts import render
from django.contrib.auth import get_user_model, authenticate, login, logout
from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views import View


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


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    # GET - доступно только залогиненным
    def get(self, request):
        return JsonResponse({
            'username': request.user.username,
            'email': request.user.email,
        })
    
from django.contrib.auth.mixins import UserPassesTestMixin

class StaffOnlyView(UserPassesTestMixin, View):
    # GET- только для staff пользователей
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return JsonResponse({'detail': 'Forbidden'}, status=403)

    def get(self, request):
        return JsonResponse({'message': 'Привет, staff!'})
    
class SessionSetView(APIView):
    #POST - сохранение значения в сессии
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        key = request.data.get('key')
        value = request.data.get('value')
        if key is None or value is None:
            return Response(
                {"detail": "Нужно передать и 'key', и 'value'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        request.session[key] = value
        return Response({"detail": f"Сохранено {key} = {value}"})

class SessionGetView(APIView):
    # GET - чтение значения из сессии
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        key = request.GET.get('key')
        if not key:
            return Response(
                {"detail": "Нужно передать параметр ?key=<имя>"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if key not in request.session:
            return Response(
                {"detail": f"В сессии нет ключа '{key}'"},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response({key: request.session[key]})

class SessionDeleteView(APIView):
    #DELETE - удаление ключа из сессии
    permission_classes = [permissions.AllowAny]

    def delete(self, request):
        key = request.GET.get('key')
        if not key:
            return Response(
                {"detail": "Нужно передать параметр ?key=<имя>"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if key not in request.session:
            return Response(
                {"detail": f"В сессии нет ключа '{key}'"},
                status=status.HTTP_404_NOT_FOUND
            )
        old = request.session.pop(key)
        return Response({key: old, "detail": "Удалено"})

class SessionExpiryView(APIView):
    #POST - установка времени жизни сессии
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        seconds = request.data.get('seconds')
        try:
            sec = int(seconds)
        except (TypeError, ValueError):
            return Response(
                {"detail": "Передайте целое число сек в поле 'seconds'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # sec == 0 — сессия до закрытия браузера; >0 — число секунд; None — по настройкам
        request.session.set_expiry(sec)
        return Response({"detail": f"Срок жизни сессии установлен: {sec} сек."})
