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
        if not request.user or not request.user.is_authenticated:
            raise PermissionDenied(
                "Authentication required.")
        item = self.get_object(pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
