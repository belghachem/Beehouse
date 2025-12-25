from django.contrib import admin
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'subject', 'created_at', 'is_read']
    list_filter = ['subject', 'is_read', 'created_at']
    search_fields = ['name', 'phone', 'message']
    readonly_fields = ['name', 'phone', 'phone', 'subject', 'message', 'created_at']
    list_editable = ['is_read']