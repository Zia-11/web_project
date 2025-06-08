from django.urls import path
from .views import UserRegistrationView, UserListView, LoginView, LogoutView, ProfileView, StaffOnlyView

urlpatterns = [
    # POST - зарегистрировать пользователя
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    # GET  - получить список пользователей
    path('users/',    UserListView.as_view(),       name='user-list'),
    path('login/',    LoginView.as_view(),  name='user-login'),
    path('logout/',   LogoutView.as_view(), name='user-logout'),
    path('profile/', ProfileView.as_view(), name='user-profile'),
    path('staff-only/', StaffOnlyView.as_view(), name='staff-only')
]
