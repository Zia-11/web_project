from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static


# настраиваем схему OpenAPI для документации
schema_view = get_schema_view(
    openapi.Info(
        title="MyProject API",
        default_version='v1',
        description="Документация для API с моделью item",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,  # документация публичная
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/', include('core.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),

    # роуты для сваггера
    path('swagger(<format>\.json|\.yaml)', schema_view.without_ui(
        cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('api/', include('core.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # для отдачи медиафайлов
