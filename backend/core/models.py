from django.db import models

# модель item - для хранения простых заметок/элементов
class Item(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # cтроковое представление - удобно для отображения в админке и shell
    def __str__(self):
        return self.title

# модель Product - для хранения информации о товаре
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, blank=True)
    quantity = models.PositiveIntegerField(default=0)

    # строковое представление - выводит название товара
    def __str__(self):
        return self.name