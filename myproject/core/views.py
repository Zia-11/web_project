from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Item
from .serializers import ItemSerializer

# Create your views here.


# APIView для списка и создания
class ItemListCreateAPIView(APIView):

    # GET - вернуть список всех Item
    def get(self, request):
        items = Item.objects.all().order_by('-created_at')
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # POST - создать новый Item
    def post(self, request):
        serializer = ItemSerializer(data=request.data)
        # is_valid() проверит обязательное поле title, типы и тд
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # если валидация не прошла - возвращаем ошибки
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# APIView для получения, обновления, удаления конкретного Item по id
class ItemRetrieveUpdateDeleteAPIView(APIView):

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
        item = self.get_object(pk)
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PATCH - частично обновить поля
    def patch(self, request, pk):
        item = self.get_object(pk)
        serializer = ItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE - удалить Item
    def delete(self, request, pk):
        item = self.get_object(pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
