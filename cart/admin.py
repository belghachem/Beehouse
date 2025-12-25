from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['get_total_price']
    
    def get_total_price(self, obj):
        return f"{obj.get_total_price()} DZD"
    get_total_price.short_description = 'Total Price'

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'get_items_count', 'get_cart_total']
    inlines = [CartItemInline]
    readonly_fields = ['created_at']
    
    def get_items_count(self, obj):
        return obj.items.count()
    get_items_count.short_description = 'Items Count'
    
    def get_cart_total(self, obj):
        total = sum(item.get_total_price() for item in obj.items.all())
        return f"{total} DZD"
    get_cart_total.short_description = 'Cart Total'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'get_total_price']
    list_filter = ['cart__user']
    
    def get_total_price(self, obj):
        return f"{obj.get_total_price()} DZD"
    get_total_price.short_description = 'Total Price'