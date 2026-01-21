from django.contrib import admin
from django.db.models import Sum
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'view_count', 'total_ordered', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['view_count', 'slug', 'created_at', 'updated_at']
    list_editable = ['price']
    ordering = ['-view_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'quantity', 'price')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Images', {
            'fields': ('picture', 'picture_2', 'picture_3'),
            'description': 'Upload up to 3 images for the product'
        }),
        ('Statistics', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_ordered(self, obj):
        """Show total quantity ordered"""
        return obj.total_ordered if hasattr(obj, 'total_ordered') else obj.get_total_ordered()
    total_ordered.short_description = 'Total Ordered'
    total_ordered.admin_order_field = 'total_ordered'
    
    def get_queryset(self, request):
        """Annotate with order statistics"""
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            total_ordered=Sum('orderitem__quantity')
        )
        return queryset
    
    # Custom actions
    actions = ['reset_view_counts', 'sort_by_most_ordered']
    
    def reset_view_counts(self, request, queryset):
        updated = queryset.update(view_count=0)
        self.message_user(request, f'{updated} products view counts reset.')
    reset_view_counts.short_description = 'Reset view counts'
    
    def sort_by_most_ordered(self, request, queryset):
        self.message_user(request, 'Sorting by most ordered products. Use column headers to sort.')
    sort_by_most_ordered.short_description = 'Sort by most ordered'
