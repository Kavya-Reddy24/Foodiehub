from django.contrib import admin
from .models import Category, FoodItem, Cart, CartItem, Order, OrderItem, UserProfile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available', 'is_vegetarian', 'is_featured']
    list_filter = ['category', 'is_available', 'is_vegetarian', 'is_featured']
    search_fields = ['name', 'description']
    list_editable = ['price', 'is_available', 'is_featured']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['food_item', 'quantity', 'price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'payment_method', 'payment_status', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_method', 'payment_status']
    search_fields = ['user__username', 'delivery_address']
    list_editable = ['status', 'payment_status']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'address']
    search_fields = ['user__username', 'phone']


admin.site.register(Cart)
admin.site.register(CartItem)

admin.site.site_header = "Food Management System Admin"
admin.site.site_title = "FMS Admin"
admin.site.index_title = "Welcome to Food Management System"
