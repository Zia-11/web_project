from rest_framework import serializers
from .models import Item
from .models import Product

# cериализатор для модели Item - преобразует объекты в JSON и обратно
class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'title', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']

# сериализатор для валидации GET-параметров
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

# сериализатор для приема и валидации HTML-строки, которую будем очищать от тегов
class SanitizeSerializer(serializers.Serializer):
    raw_html = serializers.CharField(
        help_text="HTML-текст, который нужно очистить"
    )

# сериализатор для загрузки файлов через API
class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(
        help_text="Загружаемый файл (до 2 МБ)"
    )

    # ограничиваем размер файла (максимум 2 МБ)
    def validate_file(self, f):
        limit_mb = 2
        if f.size > limit_mb * 1024 * 1024:
            raise serializers.ValidationError(f"Максимальный размер — {limit_mb} MB.")
        return f

# сериализатор для модели Product — автоматом берёт все поля
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'