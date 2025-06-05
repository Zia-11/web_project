from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from .models import Item


class ItemAPITestCase(APITestCase):
    def setUp(self):
        # создаём пользователя для аутентификации
        self.username = "testuser"
        self.password = "testpass123"
        self.user = User.objects.create_user(
            username=self.username, password=self.password)

        # получаем токен через эндпоинт /api-token-auth/
        url_token = reverse('api_token_auth')
        data = {"username": self.username, "password": self.password}
        response = self.client.post(url_token, data, format='json')
        # 200 и в ответе должен быть токен
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.token = response.data['token']

        # создаём несколько item для проверки списка и фильтрации
        Item.objects.create(title="First", description="First desc")
        Item.objects.create(title="Second", description="Second desc")
        Item.objects.create(title="Another", description="Another desc")

        # готовим клиент для аутентифицированных запросов
        self.auth_client = APIClient()
        self.auth_client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_get_item_list_public(self):
        # публичный доступ к списку (get должен вернуть все item)
        url = reverse('item-list-create')
        # без токена
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # проверяем что вернулся список из 3 объектов
        # учитывается пагинация
        self.assertEqual(len(response.data['results']), 3)
        # Проверка структуры полей
        self.assertIn('id', response.data['results'][0])
        self.assertIn('title', response.data['results'][0])
