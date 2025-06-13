from django.urls import path
from .views import(
    UserRegistrationView,
    UserListView,
    LoginView,
    LogoutView,
    ProfileView,
    StaffOnlyView, 
    SessionSetView,
    SessionGetView,
    SessionDeleteView,
    SessionExpiryView,
)
from .views import EditorOnlyView

urlpatterns = [

    # маршрут для регистрации ноового пользователя
    path('register/', UserRegistrationView.as_view(), name='user-register'),

    # маршрут для списка всех пользователей
    path('users/',    UserListView.as_view(),       name='user-list'),

    # маршрут для входа и выхода
    path('login/',    LoginView.as_view(),  name='user-login'),
    path('logout/',   LogoutView.as_view(), name='user-logout'),

    # маршрут для профиля текущего пользователя
    path('profile/',    ProfileView.as_view(),    name='user-profile'),

    # маршрут для staff
    path('staff-only/', StaffOnlyView.as_view(),  name='staff-only'),

    # маршруты для сессии
    path('session/set/',    SessionSetView.as_view(),    name='session-set'),
    path('session/get/',    SessionGetView.as_view(),    name='session-get'),
    path('session/delete/', SessionDeleteView.as_view(), name='session-delete'),
    path('session/expiry/', SessionExpiryView.as_view(), name='session-expiry'),

    # маршрут для editor
    path('editor-only/', EditorOnlyView.as_view(), name='editor-only'),
]

