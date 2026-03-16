from django.urls import path
from .views import HomeView, CategoryView, AddressView, add_address, edit_address, delete_address, ProductView, add_comment

urlpatterns = [
    path('', HomeView, name='home'),
    path('category/', CategoryView, name='category'),
    path('product_detail/<int:id>/', ProductView, name='product_detail'),
    path('product_detail/<int:id>/add_comment/', add_comment, name='add_comment'),
    path('address/', AddressView, name='address'),
    path('address/add/', add_address, name='add_address'),
    path('address/edit/<int:id>/', edit_address, name='edit_address'),
    path('address/delete/<int:id>/', delete_address, name='delete_address'),
]