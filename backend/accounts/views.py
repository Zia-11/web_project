from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.mixins import UserPassesTestMixin
from rest_framework.renderers import JSONRenderer
from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    UserSerializer,
    LoginSerializer,
    SessionSetSerializer,
    SessionExpirySerializer,
)

from .decorators import role_required
from django.utils.decorators import method_decorator

# модель пользователя
User = get_user_model()

# регистрация нового пользователя
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

# пользователи с пагинацией
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination

# вход пользователя
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Вход пользователя",
    )
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

# выход пользователя
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Выход пользователя",
    )
    def post(self, request):
        logout(request)
        return Response({'detail': 'Успешно разлогинены'})

# получение профиля текущего пользователя
class ProfileView(APIView):
    renderer_classes = [JSONRenderer]
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Получение профиля текущего пользователя",
    )
    def get(self, request):
        return Response({
            'username': request.user.username,
            'email': request.user.email,
        })

# только для пользователя с правами staff
class StaffOnlyView(UserPassesTestMixin, APIView):

    # проверка на staff
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return Response({'detail': 'Forbidden'}, status=403)

    @swagger_auto_schema(
        operation_summary="Для staff-пользователей",
    )
    def get(self, request):
        return Response({'message': 'Привет, staff!'})

# сохранение значения в сессию
class SessionSetView(APIView):

    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Сохранение значения в сессии",
    )

    # сохраняет переданную пару key-value в сессию пользователя
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

# получение значения из сессии по ключу
class SessionGetView(APIView):

    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Получение значения из сессии",
        manual_parameters=[
            openapi.Parameter(
                'key',
                openapi.IN_QUERY,
                description="Имя ключа в сессии",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ]
    )

    # возвращает значение из сессии по ключу 
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

# удаление ключа из сессии
class SessionDeleteView(APIView):

    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Удалить ключ из сессии",
        manual_parameters=[
            openapi.Parameter(
                'key',
                openapi.IN_QUERY,
                description="Имя ключа для удаления",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ]
    )
    def delete(self, request):
        key = request.GET.get('key') or request.data.get('key')
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

# установка времени жизни сессии
class SessionExpiryView(APIView):

    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Установить время жизни сессии",
    )
    def post(self, request):
        seconds = request.data.get('seconds')
        try:
            sec = int(seconds)
        except (TypeError, ValueError):
            return Response(
                {"detail": "Передайте целое число сек в поле 'seconds'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        request.session.set_expiry(sec)
        return Response({"detail": f"Срок жизни сессии установлен: {sec} сек."})

# доступ только для пользователей с ролью editor
@method_decorator(role_required('editor'), name='dispatch')
class EditorOnlyView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Только для editor",
    )
    def get(self, request):
        return Response({'message': 'Welcome, editor!'})
