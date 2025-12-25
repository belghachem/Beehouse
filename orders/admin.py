from django.contrib import admin
from django.urls import path
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Order, OrderItem, ShippingRate, StopDesk
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from twilio.rest import Client

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

def send_order_shipped(phone, order_id, tracking_number=None):
    """Send SMS when order is shipped"""
    try:
        account_sid = 'AC21caa82c442b0b6a9cbcbc8a44e729fb'  
        auth_token = '0d5ee1af090805f6c7954078d5471be2'
        client = Client(account_sid, auth_token)
        phone = clean_phone_number(phone)
        
        message = f"🚚 Good news! Your Bee House order #{order_id} has been shipped!"
        if tracking_number:
            message += f" Track it: {tracking_number}"
        
        client.messages.create(
            body=message,
            from_='+14197076659',  
            to=phone
        )
        return True
    except Exception as e:
        print(f"SMS Error: {e}")
        return False

def send_order_cancelled(phone, order_id):
    """Send SMS when order is cancelled"""
    try:
        account_sid = 'AC21caa82c442b0b6a9cbcbc8a44e729fb'
        auth_token = '0d5ee1af090805f6c7954078d5471be2'
        client = Client(account_sid, auth_token)
        phone = clean_phone_number(phone)
        
        client.messages.create(
            body=f"❌ Your Bee House order #{order_id} has been cancelled. Contact us if you have questions.",
            from_='+14197076659',
            to=phone
        )
        return True
    except Exception as e:
        print(f"SMS Error: {e}")
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
                'View/Print Invoice</a>'
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
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} order(s) marked as Processing')
    mark_as_processing.short_description = 'Mark selected as Processing'
    
    def mark_as_shipped(self, request, queryset):
        """Mark orders as shipped and send SMS notification"""
        updated = 0
        sms_sent = 0
        
        for order in queryset:
            # Update status
            order.status = 'shipped'
            order.save()
            updated += 1
            
            # Send SMS
            if send_order_shipped(order.phone, order.id, order.tracking_number):
                sms_sent += 1
        
        self.message_user(request, f'{updated} order(s) marked as Shipped. {sms_sent} SMS sent.')
    mark_as_shipped.short_description = 'Mark selected as Shipped (Send SMS)'
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} order(s) marked as Delivered')
    mark_as_delivered.short_description = 'Mark selected as Delivered'
    
    def mark_as_cancelled(self, request, queryset):
        """Mark orders as cancelled and send SMS notification"""
        updated = 0
        sms_sent = 0
        
        for order in queryset:
            # Update status
            order.status = 'cancelled'
            order.save()
            updated += 1
            
            # Send SMS
            if send_order_cancelled(order.phone, order.id):
                sms_sent += 1
        
        self.message_user(request, f'{updated} order(s) marked as Cancelled. {sms_sent} SMS sent.')
    mark_as_cancelled.short_description = 'Mark selected as Cancelled (Send SMS)'


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