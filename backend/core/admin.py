from django.contrib import admin
from .models import Item

# регистрируем модель в админке Django

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')
    search_fields = ('title',)
