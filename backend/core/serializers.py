from rest_framework import serializers
from .models import Item
from .models import Product


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        # перечисляем поля, которые хотим отдавать и принимать
        fields = ['id', 'title', 'description', 'created_at']
        # поле read_only делает его только для чтения
        read_only_fields = ['id', 'created_at']

class QueryParamsSerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=50,
        trim_whitespace=True,
        help_text="Имя (строка, до 50 символов)"
    )
    age = serializers.IntegerField(
        min_value=0, max_value=120,
        help_text="Возраст (число от 0 до 120)"
    )

class SanitizeSerializer(serializers.Serializer):
    # Сырый HTML-текст для очистки
    raw_html = serializers.CharField(
        help_text="HTML-текст, который нужно очистить"
    )

class FileUploadSerializer(serializers.Serializer):
    # Загружаемый файл (до 2 МБ)
    file = serializers.FileField(
        help_text="Загружаемый файл (до 2 МБ)"
    )

    def validate_file(self, f):
        # ограничиваем размер 2 МБ
        limit_mb = 2
        if f.size > limit_mb * 1024 * 1024:
            raise serializers.ValidationError(f"Максимальный размер — {limit_mb} MB.")
        return f
    
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'