from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from .models import Item

class ItemAPITestCase(APITestCase):
    def setUp(self):
        # создание обычного пользователя
        self.username = 'testuser'
        self.password = 'testpass123'
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )

        # создание несколько item
        Item.objects.create(title='First', description='Desc1')
        Item.objects.create(title='Second', description='Desc2')
        Item.objects.create(title='Third', description='Desc3')

        # неавторизованный клиент
        self.anon_client = APIClient()

        # авторизованный через сессию клиент
        self.auth_client = APIClient()
        login_successful = self.auth_client.login(username=self.username, password=self.password)
        assert login_successful, 'Не удалось залогинить тестового пользователя'

    # проверка что список item доступен анониму
    def test_get_item_list_public(self):
        url = reverse('item-list-create')
        response = self.anon_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    # проверка что аноним не может создать item
    def test_create_item_unauthorized(self):
        url = reverse('item-list-create')
        data = {'title': 'NewItem', 'description': 'NewDesc'}
        response = self.anon_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # проверка что авторизованный пользователь может создать item
    def test_create_item_authorized(self):
        url = reverse('item-list-create')
        data = {'title': 'NewItem', 'description': 'NewDesc'}
        response = self.auth_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'NewItem')
        self.assertEqual(Item.objects.count(), 4)

    # проверяка что аноним не может обновить item
    def test_update_item_unauthorized(self):
        item = Item.objects.first()
        url = reverse('item-detail', kwargs={'pk': item.pk})
        data = {'title': 'Updated'}
        response = self.anon_client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # проверка что авторизованный пользователь может обновить item
    def test_update_item_authorized(self):
        item = Item.objects.first()
        url = reverse('item-detail', kwargs={'pk': item.pk})
        data = {'title': 'Updated'}
        response = self.auth_client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.title, 'Updated')

    # проверка что аноним не может удалить item
    def test_delete_item_unauthorized(self):
        item = Item.objects.first()
        url = reverse('item-detail', kwargs={'pk': item.pk})
        response = self.anon_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # проверка что обычный пользователь не может удалить item
    def test_delete_item_authorized(self):
        item = Item.objects.first()
        url = reverse('item-detail', kwargs={'pk': item.pk})
        response = self.auth_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
