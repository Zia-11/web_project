import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Product
from asgiref.sync import sync_to_async

class ProductCountConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("products", self.channel_name)
        await self.accept()
        await self.send_count()  # Сразу отправляем текущее кол-во товаров

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("products", self.channel_name)

    async def send_count(self):
        count = await self.get_count()
        await self.send(text_data=json.dumps({"count": count}))

    @staticmethod
    async def get_count():
        return await sync_to_async(Product.objects.count)()

    async def receive(self, text_data):
        pass 

    async def product_count_update(self, event):
        count = event['count']
        await self.send(text_data=json.dumps({"count": count}))
