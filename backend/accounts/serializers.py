from django.contrib.auth import get_user_model
from rest_framework import serializers

# модель пользователя
User = get_user_model()

# сериализатор для пользователя
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'is_staff')

    # метод создания пользователя.
    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )

# сериализатор для входа пользователя
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

# сериализатор для установки значения в сессию
class SessionSetSerializer(serializers.Serializer):
    key = serializers.CharField(help_text="Имя ключа в сессии")
    value = serializers.CharField(help_text="Значение для сохранения")

# сериализатор для установки времени жизни сессии
class SessionExpirySerializer(serializers.Serializer):
    seconds = serializers.IntegerField()