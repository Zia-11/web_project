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
