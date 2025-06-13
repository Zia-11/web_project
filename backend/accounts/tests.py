from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from rest_framework.test import APITestCase
from rest_framework import status

import os

# модель пользователя
User = get_user_model()

# тесты на авторизацию, логаут, работу с сессией
class AccountsSessionCleaningTests(APITestCase):

    # создаём тестового пользователя
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='pass123', email='u@e.com'
        )

    # проверяем работу логина, логаута и доступ к защищённому профилю
    def test_authentication_login_logout(self):
        # логин
        url_login = reverse('user-login')
        resp = self.client.post(url_login, {'username': 'testuser', 'password': 'pass123'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('sessionid', resp.cookies)

        # доступ к профилю
        url_profile = reverse('user-profile')
        resp = self.client.get(url_profile)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['username'], 'testuser')

        # логаут
        url_logout = reverse('user-logout')
        resp = self.client.post(url_logout)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # после логаута доступ к профилю должен быть закрыт
        resp = self.client.get(url_profile)
        self.assertIn(resp.status_code, [302, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    # проверяем установку, получение, удаление и срок действия значения в сессии
    def test_session_set_get_delete_and_expiry(self):

        # установка значения в сессию
        url_set = reverse('session-set')
        resp = self.client.post(url_set, {'key': 'foo', 'value': 'bar'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # получение значения из сессии
        url_get = reverse('session-get')
        resp = self.client.get(url_get, {'key': 'foo'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get('foo'), 'bar')

        # удаление значения из сессии
        url_del = reverse('session-delete')
        resp = self.client.delete(url_del, {'key': 'foo'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get('foo'), 'bar')

        # установка времени жизни сессии
        url_exp = reverse('session-expiry')
        resp = self.client.post(url_exp, {'seconds': 5}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # проверить время жизни
        self.assertTrue(self.client.session.get_expiry_age() <= 5)

# тесты на очистку и валидацию входных данных
class RequestCleaningTests(APITestCase):

    # проверка сериализатора
    def test_validate_query_params(self):
        url = reverse('validate-query')

        # валидные параметры
        resp = self.client.get(url, {'name': 'Alice', 'age': 30})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, {'name': 'Alice', 'age': 30})

        # невалидный возраст
        resp = self.client.get(url, {'name': 'Bob', 'age': 'abc'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # проверяем очистку HTML - должны убраться теги и скрипты
    def test_sanitize_input(self):
        url = reverse('sanitize')
        raw = '<b>Bold</b><script>alert("xss")</script>'
        resp = self.client.post(url, {'raw_html': raw}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertNotIn('<', resp.data.get('cleaned_text', ''))
        self.assertIn('Bold', resp.data['cleaned_text'])

    # проверка на загрузку файла и ограничение размера файла (не больше 2 мб)
    def test_file_upload_and_validation(self):
        url = reverse('upload-file')
        content = b'testdata'
        f = SimpleUploadedFile('test.txt', content, content_type='text/plain')
        resp = self.client.post(url, {'file': f}, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.data
        self.assertIn('file_url', data)
        upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'test.txt')
        self.assertTrue(os.path.exists(upload_path))

        # тест ограничения размера
        big = SimpleUploadedFile('big.bin', b'x' * (2*1024*1024 + 1), content_type='application/octet-stream')
        resp = self.client.post(url, {'file': big}, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
