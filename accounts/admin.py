from django.contrib import admin
from .models import User, Address

class AddressInline(admin.TabularInline):
    model = Address
    extra = 1

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'first_name', 'last_name', 'email', 'phone_number')
    search_fields = ('email', 'first_name', 'last_name')
    inlines = [AddressInline]

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'label', 'street_line_1', 'city', 'state', 'postal_code', 'is_default')
    list_filter = ('label', 'is_default', 'city')
    search_fields = ('city', 'postal_code')
