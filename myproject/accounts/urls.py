from django.urls import path
from .views import UserRegistrationView, UserListView

urlpatterns = [
    # POST - зарегистрировать пользователя
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    # GET  - получить список пользователей
    path('users/',    UserListView.as_view(),       name='user-list'),
]
