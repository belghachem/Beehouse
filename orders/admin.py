from django.contrib import admin
from django.utils import timezone
from django.urls import reverse
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Order, OrderItem, ShippingRate, StopDesk
from users.models import SMSMessage
import logging

logger = logging.getLogger(__name__)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price', 'get_total_price']
    can_delete = False
    
    def get_total_price(self, obj):
        return f"{obj.get_total_price()} DA"
    get_total_price.short_description = 'Total'


def send_order_sms(phone, message):
    """Helper function to create SMS in database"""
    try:
        # Clean phone number
        phone = str(phone).replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        if phone.startswith('00213'):
            phone = '+' + phone[2:]
        elif phone.startswith('0'):
            phone = '+213' + phone[1:]
        elif phone.startswith('213'):
            phone = '+' + phone
        elif not phone.startswith('+'):
            phone = '+213' + phone
        
        # Create SMS message - your phone will send it
        sms = SMSMessage.objects.create(
            phone_number=phone,
            message=message,
            status='pending'
        )
        
        logger.info(f"SMS queued for order notification. ID: {sms.id}, Phone: {phone}")
        return True
        
    except Exception as e:
        logger.error(f"SMS Error: {str(e)}")
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'status', 'delivery_type', 
        'total_price', 'wilaya', 'created_at', 'view_invoice_button'
    ]
    list_filter = ['status', 'delivery_type', 'wilaya', 'created_at']
    search_fields = ['id', 'user__username', 'phone', 'full_name', 'tracking_number']
    readonly_fields = ['created_at', 'updated_at', 'subtotal', 'total_price','view_invoice_link',  
        'order_details_summary']
    
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'user', 'status', 'payment_method', 'tracking_number', 'view_invoice_link')
        }),
        ('Customer Details', {
            'fields': ('full_name', 'phone', 'address', 'city', 'wilaya')
        }),
        ('Delivery', {
            'fields': ('delivery_type', 'stop_desk', 'latitude', 'longitude')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'shipping_cost', 'total_price')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
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
        updated = queryset.update(status='processing', updated_at=timezone.now())
        self.message_user(request, f'{updated} order(s) marked as processing.')
    mark_as_processing.short_description = 'Mark as Processing'
    
    def mark_as_shipped(self, request, queryset):
        """Mark orders as shipped and send SMS"""
        for order in queryset:
            order.status = 'shipped'
            order.updated_at = timezone.now()
            order.save()
            
            # Send SMS notification
            tracking_info = f"Tracking: {order.tracking_number}" if order.tracking_number else ""
            message = (
                f"🐝 Bee House: Your order #{order.id} has been shipped! "
                f"{tracking_info} "
                f"Thank you for shopping with us!"
                f"viste https://beehouse-0s4k.onrender.com/users/profile/#orders"
            )
            
            try:
                send_order_sms(order.phone, message)
                logger.info(f"SMS queued for shipped order #{order.id}")
            except Exception as e:
                logger.error(f"Failed to queue SMS for order #{order.id}: {str(e)}")
        
        self.message_user(request, f'{queryset.count()} order(s) marked as shipped. SMS notifications queued.')
    mark_as_shipped.short_description = 'Mark as Shipped (Send SMS)'
    
    def mark_as_delivered(self, request, queryset):
        """Mark orders as delivered and send SMS"""
        for order in queryset:
            order.status = 'delivered'
            order.updated_at = timezone.now()
            order.save()
            
            # Send SMS notification
            message = (
                f"🐝 Bee House: Your order #{order.id} has been delivered! "
                f"We hope you enjoy your purchase. "
                f"Thank you for choosing Bee House! "
                f"viste https://beehouse-0s4k.onrender.com/users/profile/#orders"
            )
            
            try:
                send_order_sms(order.phone, message)
                logger.info(f"SMS queued for delivered order #{order.id}")
            except Exception as e:
                logger.error(f"Failed to queue SMS for order #{order.id}: {str(e)}")
        
        self.message_user(request, f'{queryset.count()} order(s) marked as delivered. SMS notifications queued.')
    mark_as_delivered.short_description = 'Mark as Delivered (Send SMS)'
    
    def mark_as_cancelled(self, request, queryset):
        """Mark orders as cancelled and send SMS"""
        for order in queryset:
            order.status = 'cancelled'
            order.updated_at = timezone.now()
            order.save()
            
            # Send SMS notification
            message = (
                f"🐝 Bee House: Your order #{order.id} has been cancelled. "
                f"If you have any questions, please contact us. "
                f"We hope to serve you again soon."
                f"viste https://beehouse-0s4k.onrender.com/users/profile/#orders"
            )
            
            try:
                send_order_sms(order.phone, message)
                logger.info(f"SMS queued for cancelled order #{order.id}")
            except Exception as e:
                logger.error(f"Failed to queue SMS for order #{order.id}: {str(e)}")
        
        self.message_user(request, f'{queryset.count()} order(s) marked as cancelled. SMS notifications queued.')
    mark_as_cancelled.short_description = 'Mark as Cancelled (Send SMS)'


@admin.register(ShippingRate)
class ShippingRateAdmin(admin.ModelAdmin):
    list_display = ['wilaya', 'home_delivery_price', 'stop_desk_price', 'return_cost']
    search_fields = ['wilaya']
    list_editable = ['home_delivery_price', 'stop_desk_price', 'return_cost']


@admin.register(StopDesk)
class StopDeskAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'wilaya', 'phone', 'is_active']
    list_filter = ['wilaya', 'is_active']
    search_fields = ['name', 'city', 'wilaya', 'address']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Location Information', {
            'fields': ('name', 'wilaya', 'city', 'address', 'phone')
        }),
        ('Map Coordinates', {
            'fields': ('latitude', 'longitude')
        }),
        ('Working Hours', {
            'fields': ('working_hours', 'working_days')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )