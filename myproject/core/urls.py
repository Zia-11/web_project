from django.urls import path, include
from .views import ItemListCreateAPIView, ItemRetrieveUpdateDeleteAPIView

urlpatterns = [
    path('items/', ItemListCreateAPIView.as_view(), name='item-list-create'),
    path('items/<int:pk>/', ItemRetrieveUpdateDeleteAPIView.as_view(),
         name='item-detail'),
]
