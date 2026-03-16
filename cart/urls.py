from django.urls import path
from .views import add_to_cart, delete_to_cart, delete_cart_item_1, CartView, delete_user_cart

urlpatterns = [
    path('add/<int:prod_id>/', add_to_cart, name='add_to_cart'),
    path('delete_item/<int:prod_id>/', delete_to_cart, name='delete_to_cart'),
    path('delete_quantity/<int:prod_id>/', delete_cart_item_1, name='delete_cart_item_1'),
    path('clear/', delete_user_cart, name='clear_cart'),
    path('', CartView, name='cart'),
]
