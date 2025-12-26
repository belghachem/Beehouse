from django.contrib import admin
from django.urls import path
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Order, OrderItem, ShippingRate, StopDesk
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.conf import settings
from twilio.rest import Client
import logging

# Set up logging
logger = logging.getLogger(__name__)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity', 'get_total_price')
    can_delete = False
    
    def get_total_price(self, obj):
        return f"{obj.get_total_price()} DZD"
    get_total_price.short_description = 'Total'

# SMS Helper Functions
def clean_phone_number(phone):
    """Convert Algerian phone to +213XXXXXXXXX format"""
    phone = str(phone).replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    if phone.startswith('00213'):
        phone = '+' + phone[2:]
    elif phone.startswith('0'):
        phone = '+213' + phone[1:]
    elif phone.startswith('213'):
        phone = '+' + phone
    elif not phone.startswith('+'):
        phone = '+213' + phone
    
    return phone

def get_twilio_client():
    """Create and return Twilio client using settings from .env"""
    try:
        # Check if using API Key or Auth Token
        if hasattr(settings, 'SMS_API_KEY_SID') and settings.SMS_API_KEY_SID:
            # Using API Key (more secure)
            client = Client(
                settings.SMS_API_KEY_SID,
                settings.SMS_API_KEY_SECRET,
                settings.SMS_ACCOUNT_SID
            )
            logger.info("Twilio client created with API Key")
        else:
            # Using Auth Token
            client = Client(
                settings.SMS_ACCOUNT_SID,
                settings.SMS_AUTH_TOKEN
            )
            logger.info("Twilio client created with Auth Token")
        return client
    except Exception as e:
        logger.error(f"Failed to create Twilio client: {e}")
        return None

def send_order_shipped(phone, order_id, tracking_number=None):
    """Send SMS when order is shipped"""
    
    # Check if SMS is enabled
    if not getattr(settings, 'SMS_ENABLED', True):
        logger.info(f"SMS disabled - Would send shipped notification for order #{order_id} to {phone}")
        print(f"📱 SMS DISABLED - Order #{order_id} shipped notification for {phone}")
        if tracking_number:
            print(f"   Tracking: {tracking_number}")
        return True
    
    try:
        client = get_twilio_client()
        if not client:
            logger.error("Failed to create Twilio client")
            return False
        
        phone = clean_phone_number(phone)
        
        message_body = f"🚚 Good news! Your Bee House order #{order_id} has been shipped!"
        if tracking_number:
            message_body += f" Track it: {tracking_number}"
        
        message = client.messages.create(
            body=message_body,
            from_=settings.SMS_TWILIO_NUMBER,
            to=phone
        )
        
        logger.info(f"Shipped SMS sent successfully to {phone}. SID: {message.sid}")
        return True
        
    except Exception as e:
        logger.error(f"SMS Error (shipped): {e}")
        print(f"❌ SMS Error: {e}")
        return False

def send_order_cancelled(phone, order_id):
    """Send SMS when order is cancelled"""
    
    # Check if SMS is enabled
    if not getattr(settings, 'SMS_ENABLED', True):
        logger.info(f"SMS disabled - Would send cancelled notification for order #{order_id} to {phone}")
        print(f"📱 SMS DISABLED - Order #{order_id} cancelled notification for {phone}")
        return True
    
    try:
        client = get_twilio_client()
        if not client:
            logger.error("Failed to create Twilio client")
            return False
        
        phone = clean_phone_number(phone)
        
        message = client.messages.create(
            body=f"❌ Your Bee House order #{order_id} has been cancelled. Contact us if you have questions.",
            from_=settings.SMS_TWILIO_NUMBER,
            to=phone
        )
        
        logger.info(f"Cancelled SMS sent successfully to {phone}. SID: {message.sid}")
        return True
        
    except Exception as e:
        logger.error(f"SMS Error (cancelled): {e}")
        print(f"❌ SMS Error: {e}")
        return False

def send_order_delivered(phone, order_id):
    """Send SMS when order is delivered"""
    
    # Check if SMS is enabled
    if not getattr(settings, 'SMS_ENABLED', True):
        logger.info(f"SMS disabled - Would send delivered notification for order #{order_id} to {phone}")
        print(f"📱 SMS DISABLED - Order #{order_id} delivered notification for {phone}")
        return True
    
    try:
        client = get_twilio_client()
        if not client:
            logger.error("Failed to create Twilio client")
            return False
        
        phone = clean_phone_number(phone)
        
        message = client.messages.create(
            body=f"✅ Your Bee House order #{order_id} has been delivered! Enjoy your products! 🐝",
            from_=settings.SMS_TWILIO_NUMBER,
            to=phone
        )
        
        logger.info(f"Delivered SMS sent successfully to {phone}. SID: {message.sid}")
        return True
        
    except Exception as e:
        logger.error(f"SMS Error (delivered): {e}")
        print(f"❌ SMS Error: {e}")
        return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'full_name',
        'phone',
        'wilaya',
        'status',
        'total_price',
        'created_at',
        'view_invoice_button'
    ]
    
    list_filter = ['status', 'created_at', 'wilaya', 'delivery_type']
    
    search_fields = ['id', 'user__username', 'full_name', 'phone']
    
    readonly_fields = [
        'user',
        'created_at',
        'updated_at',
        'total_price',
        'subtotal',
        'shipping_cost',
        'view_invoice_link',  
        'order_details_summary'
    ]
    
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'user', 'status', 'created_at', 'updated_at', 'view_invoice_link')
        }),
        ('Customer Details', {
            'fields': ('full_name', 'phone')
        }),
        ('Delivery Information', {
            'fields': ('delivery_type', 'address', 'city', 'wilaya', 'latitude', 'longitude', 'stop_desk')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'shipping_cost', 'total_price')
        }),
        ('Tracking', {
            'fields': ('tracking_number',)
        }),
        ('Order Summary', {
            'fields': ('order_details_summary',),
            'classes': ('collapse',)
        })
    )

    def view_invoice_button(self, obj):
        """Displays a button in the admin list view to open invoice"""
        url = reverse('orders:download_invoice', args=[obj.id])
        return format_html(
            '<a class="button" href="{}" target="_blank" '
            'style="color: white; padding: 5px 10px; background: #417690; '
            'text-decoration: none; border-radius: 4px; font-weight: bold;">'
            'View Invoice</a>',
            url
        )
    view_invoice_button.short_description = 'Invoice'
    view_invoice_button.allow_tags = True
    
    def view_invoice_link(self, obj):
        """Displays a large clickable link in the detail view"""
        if obj.id:
            url = reverse('orders:download_invoice', args=[obj.id])
            return format_html(
                '<div style="background: #f0f0f0; padding: 20px; border-radius: 8px; text-align: center;">'
                '<a href="{}" target="_blank" '
                'style="background: #417690; color: white; padding: 15px 40px; text-decoration: none; '
                'border-radius: 10px; font-size: 16px; font-weight: bold; '
                'display: inline-block; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);">'
                '📄 View/Print Invoice</a>'
                '<p style="margin-top: 15px; color: #666; font-size: 14px;">'
                'Click to view the printable invoice in a new tab</p>'
                '</div>',
                url
            )
        return "Save order first to generate invoice"
    view_invoice_link.short_description = 'Invoice Actions'
    
    def order_details_summary(self, obj):
        """Displays formatted order items in admin"""
        items_html = '<div style="background: white; padding: 15px; border-radius: 8px;">'
        items_html += '<h3 style="color: #333; margin-bottom: 15px;">Order Items</h3>'
        items_html += '<table style="width: 100%; border-collapse: collapse;">'
        items_html += '''
            <thead style="background: #f59e0b; color: white;">
                <tr>
                    <th style="padding: 10px; text-align: left;">Product</th>
                    <th style="padding: 10px; text-align: center;">Quantity</th>
                    <th style="padding: 10px; text-align: right;">Price</th>
                    <th style="padding: 10px; text-align: right;">Total</th>
                </tr>
            </thead>
            <tbody>
        '''
        
        for item in obj.items.all():
            items_html += f'''
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 10px;">{item.product.name}</td>
                    <td style="padding: 10px; text-align: center;">{item.quantity}</td>
                    <td style="padding: 10px; text-align: right;">{item.price} DZD</td>
                    <td style="padding: 10px; text-align: right; font-weight: bold; color: #d97706;">
                        {item.get_total_price()} DZD
                    </td>
                </tr>
            '''
        
        items_html += '</tbody></table></div>'
        return mark_safe(items_html)
    order_details_summary.short_description = 'Order Items'
    
    # ========== Actions ==========
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    
    def mark_as_processing(self, request, queryset):
        """Mark orders as processing"""
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} order(s) marked as Processing ⏳')
    mark_as_processing.short_description = '⏳ Mark selected as Processing'
    
    def mark_as_shipped(self, request, queryset):
        """Mark orders as shipped and send SMS notification"""
        updated = 0
        sms_sent = 0
        sms_failed = 0
        
        for order in queryset:
            # Update status
            order.status = 'shipped'
            order.save()
            updated += 1
            
            # Send SMS
            if send_order_shipped(order.phone, order.id, order.tracking_number):
                sms_sent += 1
            else:
                sms_failed += 1
        
        # Build message
        msg = f'{updated} order(s) marked as Shipped 🚚'
        if getattr(settings, 'SMS_ENABLED', True):
            msg += f' | {sms_sent} SMS sent ✅'
            if sms_failed > 0:
                msg += f' | {sms_failed} SMS failed ❌'
        else:
            msg += ' | SMS notifications disabled in settings'
        
        self.message_user(request, msg)
    mark_as_shipped.short_description = '🚚 Mark selected as Shipped (Send SMS)'
    
    def mark_as_delivered(self, request, queryset):
        """Mark orders as delivered and send SMS notification"""
        updated = 0
        sms_sent = 0
        sms_failed = 0
        
        for order in queryset:
            # Update status
            order.status = 'delivered'
            order.save()
            updated += 1
            
            # Send SMS
            if send_order_delivered(order.phone, order.id):
                sms_sent += 1
            else:
                sms_failed += 1
        
        # Build message
        msg = f'{updated} order(s) marked as Delivered ✅'
        if getattr(settings, 'SMS_ENABLED', True):
            msg += f' | {sms_sent} SMS sent ✅'
            if sms_failed > 0:
                msg += f' | {sms_failed} SMS failed ❌'
        else:
            msg += ' | SMS notifications disabled in settings'
        
        self.message_user(request, msg)
    mark_as_delivered.short_description = '✅ Mark selected as Delivered (Send SMS)'
    
    def mark_as_cancelled(self, request, queryset):
        """Mark orders as cancelled and send SMS notification"""
        updated = 0
        sms_sent = 0
        sms_failed = 0
        
        for order in queryset:
            # Update status
            order.status = 'cancelled'
            order.save()
            updated += 1
            
            # Send SMS
            if send_order_cancelled(order.phone, order.id):
                sms_sent += 1
            else:
                sms_failed += 1
        
        # Build message
        msg = f'{updated} order(s) marked as Cancelled ❌'
        if getattr(settings, 'SMS_ENABLED', True):
            msg += f' | {sms_sent} SMS sent ✅'
            if sms_failed > 0:
                msg += f' | {sms_failed} SMS failed ❌'
        else:
            msg += ' | SMS notifications disabled in settings'
        
        self.message_user(request, msg)
    mark_as_cancelled.short_description = '❌ Mark selected as Cancelled (Send SMS)'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'get_total_price']
    list_filter = ['order__status']
    search_fields = ['order__id', 'product__name']

@admin.register(StopDesk)
class StopDeskAdmin(admin.ModelAdmin):
    list_display = ['name', 'wilaya', 'city', 'phone', 'is_active']
    list_filter = ['wilaya', 'is_active']
    search_fields = ['name', 'wilaya', 'city', 'address']
    ordering = ['wilaya', 'city', 'name']
    
    fieldsets = (
        ('Location Information', {
            'fields': ('name', 'wilaya', 'city', 'address', 'phone')
        }),
        ('Map Coordinates', {
            'fields': ('latitude', 'longitude')
        }),
        ('Working Hours', {
            'fields': ('working_hours', 'working_days', 'is_active')
        }),
    )      

@admin.register(ShippingRate)
class ShippingRateAdmin(admin.ModelAdmin):
    list_display = ['wilaya', 'home_delivery_price', 'stop_desk_price', 'return_cost']
    list_filter = ['home_delivery_price']
    search_fields = ['wilaya']
    ordering = ['wilaya']
