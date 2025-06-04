from rest_framework import serializers
from .models import Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        # перечисляем поля, которые хотим отдавать и принимать
        fields = ['id', 'title', 'description', 'created_at']
        # поле read_only делает его только для чтения
        read_only_fields = ['id', 'created_at']
