from django.contrib import admin
from .models import UserProfile, Wishlist, SMSMessage

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone']

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'added_date']
    list_filter = ['added_date']

@admin.register(SMSMessage)
class SMSMessageAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'status', 'created_at', 'sent_at']
    list_filter = ['status', 'created_at']
    search_fields = ['phone_number', 'message']
    readonly_fields = ['created_at', 'sent_at']