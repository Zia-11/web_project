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
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('users/',    UserListView.as_view(),       name='user-list'),

    path('login/',    LoginView.as_view(),  name='user-login'),
    path('logout/',   LogoutView.as_view(), name='user-logout'),

    path('profile/',    ProfileView.as_view(),    name='user-profile'),
    path('staff-only/', StaffOnlyView.as_view(),  name='staff-only'),

    path('session/set/',    SessionSetView.as_view(),    name='session-set'),
    path('session/get/',    SessionGetView.as_view(),    name='session-get'),
    path('session/delete/', SessionDeleteView.as_view(), name='session-delete'),
    path('session/expiry/', SessionExpiryView.as_view(), name='session-expiry'),

    path('editor-only/', EditorOnlyView.as_view(), name='editor-only'),
]

