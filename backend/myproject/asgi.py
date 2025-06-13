import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import myproject.routing

# переменная окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# основное ASGI-приложение
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            myproject.routing.websocket_urlpatterns
        )
    ),
})