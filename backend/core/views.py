import os

# django
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.utils.html import strip_tags

# rest
from rest_framework import status, permissions, filters, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny

# filters
from django_filters.rest_framework import DjangoFilterBackend

# swagger
from drf_yasg.utils import swagger_auto_schema

# models/serializers
from .models import Item, Product
from .serializers import (
    ItemSerializer,
    ProductSerializer,
    QueryParamsSerializer,
    SanitizeSerializer,
    FileUploadSerializer,
)

# класс для списка и создания item
class ItemListCreateAPIView(APIView):
    # доступно всем пользователям
    permission_classes = [AllowAny]

    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['created_at'] #фильтр по дате создания
    search_fields = ['title', 'description'] #поиск по названию и описанию
    ordering_fields = ['created_at', 'title'] #сортировка по дате и названию

    @swagger_auto_schema(
        operation_summary="Получение списка Item",
    )
    #получение списка item
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
    )
    # создание нового item
    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            raise PermissionDenied("Требуется аутентификация")
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# класс для работы с одним item
class ItemRetrieveUpdateDeleteAPIView(APIView):

    # доступно всем
    permission_classes = [AllowAny]

    # получение item по id
    def get_object(self, pk):
        return get_object_or_404(Item, pk=pk)

    @swagger_auto_schema(
        operation_summary="Получение Item по id",
    )
    # получение и сериализация объекта
    def get(self, request, pk):
        item = self.get_object(pk)
        serializer = ItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="Полное обновление Item",
    )
    # полное обновление Item
    def put(self, request, pk):
        if not request.user or not request.user.is_authenticated:
            raise PermissionDenied("Требуется аутентификация")
        item = self.get_object(pk)
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="Частичное обновление Item",
    )
    # частичное обновление item
    def patch(self, request, pk):
        if not request.user or not request.user.is_authenticated:
            raise PermissionDenied("Требуется аутентификация")
        item = self.get_object(pk)
        serializer = ItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Удаление Item",
    )
    # удаление item
    def delete(self, request, pk):
        if not request.user.is_authenticated:
            raise PermissionDenied("Требуется аутентификация")
        if not request.user.is_staff:
            raise PermissionDenied("Только администратор может удалить этот элемент")
        item = self.get_object(pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# валидация GET-параметров через сериализатор
class ValidateQueryView(APIView):

    # любой может валидировать параметры
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Валидация GET-параметров",
    )
    def get(self, request):
        serializer = QueryParamsSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

# санитизация html
class SanitizeView(APIView):

    # любой может отправлять запрос
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Санитизация HTML",
    )
    def post(self, request):
        serializer = SanitizeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw = serializer.validated_data['raw_html']
        cleaned = strip_tags(raw)
        return Response({
            "cleaned_text": cleaned
        })

# загрузка файла
class FileUploadView(APIView):

    # любой может загружать файл
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Загрузка файла",
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
        url = request.build_absolute_uri(
            settings.MEDIA_URL + 'uploads/' + f.name
        )
        return Response({"file_url": url}, status=status.HTTP_201_CREATED)
    
# CRUD по Product через ViewSet
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'price'] # фильтрация по категории и цене
    search_fields = ['name', 'description', 'category'] # поиск по названию, описанию, категории
    ordering_fields = ['price', 'quantity', 'name'] # сортировка по цене, количеству и названию
