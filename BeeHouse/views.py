from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import timedelta
from orders.models import Order
from contactus.models import Contact
from users.models import Wishlist, SMSMessage


@staff_member_required
def admin_notifications_view(request):
    """
    Display all admin notifications organized by priority:
    - Urgent (red)
    - Important (yellow)
    - Info (blue)
    """
    
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    # URGENT NOTIFICATIONS (Red)
    urgent_notifications = []
    
    # 1. Old pending orders (>24 hours)
    old_orders = Order.objects.filter(status='pending', created_at__date__lte=yesterday)
    old_count = old_orders.count()
    if old_count > 0:
        urgent_notifications.append({
            'icon': '⚠️',
            'title': f'{old_count} pending order(s) older than 24 hours',
            'description': 'These orders need immediate processing!',
            'link': '/znd/orders/order/?status__exact=pending',
            'link_text': 'View Orders',
            'count': old_count,
        })
    
    # 2. Failed SMS
    failed_sms = SMSMessage.objects.filter(status='failed')
    failed_count = failed_sms.count()
    if failed_count > 0:
        urgent_notifications.append({
            'icon': '❌',
            'title': f'{failed_count} SMS message(s) failed to send',
            'description': 'Customer notifications were not delivered.',
            'link': '/znd/users/smsmessage/?status__exact=failed',
            'link_text': 'Retry Now',
            'count': failed_count,
        })
    
    # IMPORTANT NOTIFICATIONS (Yellow)
    important_notifications = []
    
    # 3. New pending orders (today)
    new_pending = Order.objects.filter(status='pending', created_at__date=today)
    new_pending_count = new_pending.count()
    if new_pending_count > 0:
        important_notifications.append({
            'icon': '📦',
            'title': f'{new_pending_count} new pending order(s) today',
            'description': 'These orders are waiting to be processed.',
            'link': '/znd/orders/order/?status__exact=pending',
            'link_text': 'View Orders',
            'count': new_pending_count,
        })
    
    # 4. New contact messages (today)
    today_contacts = Contact.objects.filter(is_read=False, created_at__date=today)
    today_contact_count = today_contacts.count()
    if today_contact_count > 0:
        important_notifications.append({
            'icon': '📧',
            'title': f'{today_contact_count} new contact message(s) received today',
            'description': 'Customers are waiting for your response.',
            'link': '/znd/contactus/contact/?is_read__exact=0',
            'link_text': 'Read Messages',
            'count': today_contact_count,
        })
    
    # INFO NOTIFICATIONS (Blue)
    info_notifications = []
    
    # 5. Older unread messages
    old_contacts = Contact.objects.filter(is_read=False, created_at__date__lt=today)
    old_contact_count = old_contacts.count()
    if old_contact_count > 0:
        info_notifications.append({
            'icon': '📨',
            'title': f'{old_contact_count} older unread contact message(s)',
            'description': 'These messages are from previous days.',
            'link': '/znd/contactus/contact/?is_read__exact=0',
            'link_text': 'View All',
            'count': old_contact_count,
        })
    
    # 6. Wishlist items today
    today_wishlists = Wishlist.objects.filter(added_date__date=today)
    wishlist_count = today_wishlists.count()
    if wishlist_count > 0:
        # Get product names that were wishlisted
        products = today_wishlists.values_list('product__name', flat=True)[:5]
        product_list = ', '.join(products)
        if wishlist_count > 5:
            product_list += f' and {wishlist_count - 5} more'
        
        info_notifications.append({
            'icon': '❤️',
            'title': f'{wishlist_count} customer(s) added items to wishlist today',
            'description': f'Popular items: {product_list}',
            'link': '/znd/users/wishlist/',
            'link_text': 'View Wishlists',
            'count': wishlist_count,
        })
    
    # 7. Pending SMS (waiting to be sent)
    pending_sms = SMSMessage.objects.filter(status='pending')
    pending_sms_count = pending_sms.count()
    if pending_sms_count > 0:
        info_notifications.append({
            'icon': '📱',
            'title': f'{pending_sms_count} SMS message(s) waiting to be sent',
            'description': 'Your phone will send these automatically.',
            'link': '/znd/users/smsmessage/?status__exact=pending',
            'link_text': 'View Queue',
            'count': pending_sms_count,
        })
    
    # Calculate totals
    total_urgent = len(urgent_notifications)
    total_important = len(important_notifications)
    total_info = len(info_notifications)
    total_all = total_urgent + total_important + total_info
    
    context = {
        'urgent_notifications': urgent_notifications,
        'important_notifications': important_notifications,
        'info_notifications': info_notifications,
        'total_urgent': total_urgent,
        'total_important': total_important,
        'total_info': total_info,
        'total_all': total_all,
        'has_notifications': total_all > 0,
    }
    
    return render(request, 'admin/notifications.html', context)