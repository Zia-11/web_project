from django.urls import re_path
from core.consumers import ProductCountConsumer

websocket_urlpatterns = [
    re_path(r'ws/products/count/$', ProductCountConsumer.as_asgi()),
]