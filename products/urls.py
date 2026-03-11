from django.urls import path
from .views import add_product, update, update_product, delete_product

urlpatterns = [
    path('add/', add_product, name='add_product'),
    path('update/', update, name='update_page'),
    path('update/<int:id>/', update_product, name='update_product'),
    path('delete/<int:id>/', delete_product, name='delete_product'),
]
