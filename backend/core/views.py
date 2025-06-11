from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Item
from .serializers import ItemSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
import os
from django.conf import settings
from django.utils.html import strip_tags
from rest_framework import status, permissions
from .serializers import (
    QueryParamsSerializer,
    SanitizeSerializer,
    FileUploadSerializer
)
from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer
# Create your views here.


# APIView для списка и создания
class ItemListCreateAPIView(APIView):

    # GET доступен всем, POST проверяется вручную
    permission_classes = [AllowAny]

    # GET - запрос с фильтрацией, поиском, сортировкой и пагинацией
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['created_at']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']

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

    # добавим body параметр
    @swagger_auto_schema(
            operation_description="Создать новый Item (требуется токен).",
            request_body=ItemSerializer,              
            responses={201: ItemSerializer,
                    400: 'Bad Request (Validation errors)',
                    403: 'Forbidden (если неавторизован)'}
        )

        # POST - создать новый Item
    def post(self, request):
        # проверка на аутентификацию
        if not request.user or not request.user.is_authenticated:
            raise PermissionDenied("Authentication required.")
        serializer = ItemSerializer(data=request.data)
        # is_valid() проверит обязательное поле title, типы и тд
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # если валидация не прошла - возвращаем ошибки
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# APIView для получения, обновления, удаления конкретного Item по id
class ItemRetrieveUpdateDeleteAPIView(APIView):

    # get будет разрешён без токена, все остальные проверяются вручную
    permission_classes = [AllowAny]

    # GET - вернуть объект или ошибку в противном случае
    def get_object(self, pk):
        return get_object_or_404(Item, pk=pk)

    # GET - вернуть Item по id=pk
    def get(self, request, pk):
        item = self.get_object(pk)
        serializer = ItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
            operation_description="Полностью обновить Item (PUT)",
            request_body=ItemSerializer,
            responses={200: ItemSerializer, 400: 'Bad Request', 403: 'Forbidden'}
        )    

    # PUT - полностью заменить поля Item
    def put(self, request, pk):
        if not request.user or not request.user.is_authenticated:
            raise PermissionDenied("Authentication required.")
        item = self.get_object(pk)
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Частично обновить Item (PATCH)",
        request_body=ItemSerializer,
        responses={200: ItemSerializer, 400: 'Bad Request', 403: 'Forbidden'}
    )

    # PATCH - частично обновить поля
    def patch(self, request, pk):
        if not request.user or not request.user.is_authenticated:
            raise PermissionDenied("Authentication required.")
        item = self.get_object(pk)
        serializer = ItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE - удалить Item
    def delete(self, request, pk):
        # только админ может удалять
        if not request.user.is_authenticated:
            raise PermissionDenied("Authentication required.")
        if not request.user.is_staff:
            raise PermissionDenied("Only admin can delete this item.")
        item = self.get_object(pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ValidateQueryView(APIView):
    # валидация GET-параметров через сериализатор
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        serializer = QueryParamsSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        # если валидно — вернуть очищенные данные
        return Response(serializer.validated_data)


class SanitizeView(APIView):
    # возвращает plain-text без тегов
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SanitizeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        raw = serializer.validated_data['raw_html']
        # убираем все HTML теги
        cleaned = strip_tags(raw)

        return Response({
            "cleaned_text": cleaned
        })


class FileUploadView(APIView):
    # загружает файл в MEDIA_ROOT/uploads/ и возвращает ссылку
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        f = serializer.validated_data['file']
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        path = os.path.join(upload_dir, f.name)

        # сохраняем файл
        with open(path, 'wb+') as dest:
            for chunk in f.chunks():
                dest.write(chunk)

        url = request.build_absolute_uri(
            settings.MEDIA_URL + 'uploads/' + f.name
        )
        return Response({"file_url": url}, status=status.HTTP_201_CREATED)
    
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny] 