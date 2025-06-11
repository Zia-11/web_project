from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def broadcast_product_count():
    channel_layer = get_channel_layer()
    from .models import Product
    count = Product.objects.count()
    async_to_sync(channel_layer.group_send)(
        "products",
        {
            "type": "product_count_update",
            "count": count,
        }
    )

@receiver(post_save, sender=Product)
def product_saved(sender, instance, created, **kwargs):
    broadcast_product_count()

@receiver(post_delete, sender=Product)
def product_deleted(sender, instance, **kwargs):
    broadcast_product_count()
