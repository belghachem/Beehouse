from django.contrib import admin
from django.db.models import Sum, Count
from .models import Product
from orders.models import OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
   list_display = ['name', 'category', 'quantity', 'price', 'slug']
    list_filter = ['category']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price']
    ordering = ['category', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'quantity', 'price')
        }),
        ('Details', {
            'fields': ('description',)
        }),
        ('Images', {
            'fields': ('picture', 'picture_2', 'picture_3')
        }),
        ('Statistics', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_ordered(self, obj):
        """Display total quantity ordered for this product"""
        total = OrderItem.objects.filter(product=obj).aggregate(
            total=Sum('quantity')
        )['total']
        return total if total else 0
    
    total_ordered.short_description = 'Total Ordered'
    total_ordered.admin_order_field = 'total_ordered'
    
    def get_queryset(self, request):
        """Optimize queryset with annotations"""
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            total_ordered=Sum('orderitem__quantity')
        )
        return queryset
    
    # Add custom action to reset view counts
    actions = ['reset_view_counts']
    
    def reset_view_counts(self, request, queryset):
        updated = queryset.update(view_count=0)
        self.message_user(request, f'{updated} products view counts have been reset.')
    
    reset_view_counts.short_description = 'Reset view counts for selected products'


# Custom admin view for statistics
class ProductStatisticsAdmin(admin.ModelAdmin):

    list_display = ['name', 'category', 'view_count', 'total_ordered', 'price']
    list_filter = ['category']
    search_fields = ['name']
    
    # Make everything read-only
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            total_ordered=Sum('orderitem__quantity')
        ).order_by('-total_ordered')  
        return queryset
    
    def total_ordered(self, obj):
        return obj.total_ordered if obj.total_ordered else 0
    
    total_ordered.short_description = 'Total Ordered'
    total_ordered.admin_order_field = 'total_ordered'

