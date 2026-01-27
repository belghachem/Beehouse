from django.contrib import messages
from django.utils import timezone
from django.utils.safestring import mark_safe
from datetime import timedelta
from orders.models import Order
from contactus.models import Contact
from users.models import Wishlist


class AdminNotificationMiddleware:
    """
    Middleware to show admin notifications for:
    - Pending orders
    - New contact messages
    - New wishlist items
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Only show notifications for admin users on admin pages
        if request.user.is_authenticated and request.user.is_staff and request.path.startswith('/znd/'):
            self.check_and_display_notifications(request)
        
        response = self.get_response(request)
        return response
    
    def check_and_display_notifications(self, request):
        """Check for pending tasks and display notifications"""
        
        # Get today's date
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # 1. CHECK PENDING ORDERS
        pending_orders = Order.objects.filter(status='pending')
        pending_count = pending_orders.count()
        
        if pending_count > 0:
            # Check for old orders (more than 24 hours)
            old_orders = pending_orders.filter(created_at__date__lte=yesterday)
            old_count = old_orders.count()
            
            if old_count > 0:
                messages.error(
                    request,
                    mark_safe(
                        f"🚨 URGENT: {old_count} pending order(s) are more than 24 hours old! "
                        f'<a href="/znd/orders/order/?status__exact=pending" style="color: white; text-decoration: underline;">View Now</a>'
                    )
                )
            
            if pending_count > old_count:
                new_pending = pending_count - old_count
                messages.warning(
                    request,
                    mark_safe(
                        f"📦 You have {new_pending} new pending order(s) waiting to be processed. "
                        f'<a href="/znd/orders/order/?status__exact=pending" style="color: white; text-decoration: underline;">View Orders</a>'
                    )
                )
        
        # 2. CHECK UNREAD CONTACT MESSAGES
        unread_contacts = Contact.objects.filter(is_read=False)
        unread_count = unread_contacts.count()
        
        if unread_count > 0:
            # Check for messages from today
            today_contacts = unread_contacts.filter(created_at__date=today).count()
            
            if today_contacts > 0:
                messages.warning(
                    request,
                    mark_safe(
                        f"📧 You have {today_contacts} new contact message(s) received today! "
                        f'<a href="/znd/contactus/contact/?is_read__exact=0" style="color: white; text-decoration: underline;">Read Messages</a>'
                    )
                )
            
            if unread_count > today_contacts:
                old_contacts = unread_count - today_contacts
                messages.info(
                    request,
                    mark_safe(
                        f"📨 {old_contacts} older unread contact message(s). "
                        f'<a href="/znd/contactus/contact/?is_read__exact=0" style="color: white; text-decoration: underline;">View All</a>'
                    )
                )
        
        # 3. CHECK NEW WISHLIST ITEMS (added today)
        today_wishlists = Wishlist.objects.filter(added_date__date=today)
        wishlist_count = today_wishlists.count()
        
        if wishlist_count > 0:
            messages.info(
                request,
                mark_safe(
                    f"❤️ {wishlist_count} customer(s) added items to their wishlist today! "
                    f'<a href="/znd/users/wishlist/" style="color: white; text-decoration: underline;">View Wishlists</a>'
                )
            )
        
        # 4. CHECK FAILED SMS (if any)
        from users.models import SMSMessage
        failed_sms = SMSMessage.objects.filter(status='failed').count()
        
        if failed_sms > 0:
            messages.error(
                request,
                mark_safe(
                    f"❌ {failed_sms} SMS message(s) failed to send! "
                    f'<a href="/znd/users/smsmessage/?status__exact=failed" style="color: white; text-decoration: underline;">Retry Now</a>'
                )
            )
