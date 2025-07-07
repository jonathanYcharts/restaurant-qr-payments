from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Restaurant,
    RestaurantUser,
    MenuItem,
    Order,
    OrderItem,
    RegistrationToken,
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'table_number', 'status', 'created_at']
    list_filter = ['restaurant', 'status']
    search_fields = ['table_number']
    inlines = [OrderItemInline]
    ordering = ['-created_at']
    list_select_related = ['restaurant']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant', 'price', 'available']
    list_editable = ['price', 'available']
    list_filter = ['restaurant', 'available']
    search_fields = ['name']
    list_select_related = ['restaurant']


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner_email', 'created_at']
    search_fields = ['name', 'owner_email']


@admin.register(RestaurantUser)
class RestaurantUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'restaurant', 'is_staff', 'is_active']
    list_filter = ['restaurant', 'is_staff']
    search_fields = ['username', 'email']
    list_select_related = ['restaurant']


@admin.register(RegistrationToken)
class RegistrationTokenAdmin(admin.ModelAdmin):
    list_display = ['copyable_token', 'is_used', 'created_at']
    list_filter = ['is_used']
    search_fields = ['token']
    readonly_fields = ['copyable_token', 'is_used', 'created_at']
    fields = ['copyable_token', 'is_used', 'created_at']

    def copyable_token(self, obj):
        return format_html(
            '<input type="text" value="{}" readonly style="width: 100%;" onclick="this.select();" />',
            obj.token
        )
    copyable_token.short_description = "Token"

    def has_add_permission(self, request):
        return True

    def get_changeform_initial_data(self, request):
        from uuid import uuid4
        return {'token': str(uuid4())}
