from django.contrib import admin
from .models import Product

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
        ('Description', {
            'fields': ('description',)
        }),
        ('Images', {
            'fields': ('picture', 'picture_2', 'picture_3'),
            'description': 'Upload up to 3 images for the product'
        }),
    )