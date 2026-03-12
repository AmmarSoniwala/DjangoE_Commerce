from django.urls import path
from .views import HomeView, CategoryView

urlpatterns = [
    path('', HomeView, name='home'),
    path('category/', CategoryView, name='category'),
]