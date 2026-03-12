from django.contrib import admin
from .models import Products, ProductReview
# Register your models here.

@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'price', 'category', 'stock')
    list_filter = ('category', 'stock')
    search_fields = ('name', 'brand', 'description')
    ordering = ('name',)

@admin.register(ProductReview)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'stars', 'comment', 'created_at')
    list_filter = ('stars', 'created_at')
    search_fields = ('user__username', 'product__name', 'comment')
    ordering = ('-created_at',)