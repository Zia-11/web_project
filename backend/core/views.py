import os

# django
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.html import strip_tags

# rest
from rest_framework import status, permissions, filters, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication

# filters
from django_filters.rest_framework import DjangoFilterBackend

# swagger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# models/serializers
from .models import Item, Product
from .serializers import (
    ItemSerializer,
    ProductSerializer,
    QueryParamsSerializer,
    SanitizeSerializer,
    FileUploadSerializer,
)


class PingView(APIView):
    def get(self, request):
        # просто отдаём фиксированный JSON
        return Response({"status": "ok", "message": "pong"})


# класс для списка и создания item
class ItemListCreateAPIView(APIView):
    # доступно всем пользователям
    permission_classes = [AllowAny]

    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['created_at']  # фильтр по дате создания
    search_fields = ['title', 'description']  # поиск по названию и описанию
    ordering_fields = ['created_at', 'title']  # сортировка по дате и названию

    @swagger_auto_schema(
        operation_summary="Получение списка Item с фильтрацией/поиском/сортировкой",
        manual_parameters=[
            openapi.Parameter(
                'created_at',
                openapi.IN_QUERY,
                description="Фильтр по дате создания (YYYY-MM-DD или диапазон)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Поиск по title или description",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                description="Сортировка: передайте поле, например `created_at` или `-title`",
                type=openapi.TYPE_STRING,
            ),
        ]
    )
    def get(self, request):
        qs = Item.objects.all().order_by('-created_at')
        for backend in self.filter_backends:
            qs = backend().filter_queryset(request, qs, view=self)
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        if page is not None:
            serializer = ItemSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = ItemSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Создание нового Item",
        request_body=ItemSerializer
    )
    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            raise PermissionDenied("Требуется аутентификация")
        serializer = ItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# класс для работы с одним item
class ItemRetrieveUpdateDeleteAPIView(APIView):
    # поддерживаем сессионную basic и token-аутентификацию
    authentication_classes = [SessionAuthentication, BasicAuthentication, TokenAuthentication]
    # по умолчанию доступно всем метод DELETE будет проверять IsAdminUser
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        return [permission() for permission in self.permission_classes]

    def get_object(self, pk):
        return get_object_or_404(Item, pk=pk)

    @swagger_auto_schema(
        operation_summary="Получение Item по id",
    )
    def get(self, request, pk):
        item = self.get_object(pk)
        serializer = ItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Полное обновление Item",
        request_body=ItemSerializer
    )
    def put(self, request, pk):
        if not request.user or not request.user.is_authenticated:
            raise PermissionDenied("Требуется аутентификация")
        required_fields = ['title', 'description']
        for field in required_fields:
            if field not in request.data:
                return Response(
                    {"detail": f"Отсутствует обязательное поле: {field}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        item = self.get_object(pk)
        serializer = ItemSerializer(item, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Частичное обновление Item",
        request_body=ItemSerializer,
    )
    def patch(self, request, pk):
        if not request.user or not request.user.is_authenticated:
            raise PermissionDenied("Требуется аутентификация")
        item = self.get_object(pk)
        serializer = ItemSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Удаление Item",
    )
    def delete(self, request, pk):
        # сюда попадут только staff-пользователи благодаря IsAdminUser
        item = self.get_object(pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# валидация GET-параметров через сериализатор

class ValidateQueryView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Валидация GET-параметров",
        query_serializer=QueryParamsSerializer,
        responses={200: openapi.Response('Валидированные параметры', QueryParamsSerializer)}
    )
    def get(self, request):
        serializer = QueryParamsSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

# санитизация html

class SanitizeView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Санитизация HTML",
        request_body=SanitizeSerializer,
        responses={200: openapi.Response('Очищённый текст', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'cleaned_text': openapi.Schema(type=openapi.TYPE_STRING)}
        ))}
    )
    def post(self, request):
        serializer = SanitizeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cleaned = strip_tags(serializer.validated_data['raw_html'])
        return Response({"cleaned_text": cleaned})

# загрузка файла

class FileUploadView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_summary="Загрузка файла",
        request_body=FileUploadSerializer,
        responses={201: openapi.Response(
            description="URL загруженного файла",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'file_url': openapi.Schema(type=openapi.TYPE_STRING)}
            )
        )}
    )
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        f = serializer.validated_data['file']

        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        path = os.path.join(upload_dir, f.name)
        with open(path, 'wb+') as dest:
            for chunk in f.chunks():
                dest.write(chunk)

        url = request.build_absolute_uri(settings.MEDIA_URL + 'uploads/' + f.name)
        return Response({"file_url": url}, status=status.HTTP_201_CREATED)
    
# CRUD по Product через ViewSet

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'price']
    search_fields = ['name', 'description', 'category']
    ordering_fields = ['price', 'quantity', 'name']
