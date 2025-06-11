from django.urls import path, include
from .views import (
    ItemListCreateAPIView,
    ItemRetrieveUpdateDeleteAPIView,
    ValidateQueryView,
    SanitizeView,
    FileUploadView,
)
urlpatterns = [
    path('items/', ItemListCreateAPIView.as_view(), name='item-list-create'),
    path('items/<int:pk>/', ItemRetrieveUpdateDeleteAPIView.as_view(),
         name='item-detail'),
    # для обработки запросов
    path('clean/validate-query/', ValidateQueryView.as_view(), name='validate-query'),
    path('clean/sanitize/',       SanitizeView.as_view(),      name='sanitize'),
    path('clean/upload-file/',    FileUploadView.as_view(),    name='upload-file')
]
