import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Product
from asgiref.sync import sync_to_async

# WebSocket consumer - класс для отправки количества товаров в реальном времени
class ProductCountConsumer(AsyncWebsocketConsumer):

    # метод вызывается при новом подключении по WebSocket
    async def connect(self):
        await self.channel_layer.group_add("products", self.channel_name)
        await self.accept()
        await self.send_count()

    # метод вызывается при отключении клиента
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("products", self.channel_name)

    # метод для отправки клиенту актуального количества товаров
    async def send_count(self):
        count = await self.get_count()
        await self.send(text_data=json.dumps({"count": count}))

    # асинхронный статический метод для получения количества товаров в базе
    @staticmethod
    async def get_count():
        return await sync_to_async(Product.objects.count)()

    # метод вызывается, когда клиент присылает данные по WebSocket
    async def receive(self, text_data):
        pass 

    # метод вызывается при получении сообщения типа "product_count_update" из группы
    async def product_count_update(self, event):
        count = event['count']
        await self.send(text_data=json.dumps({"count": count}))
