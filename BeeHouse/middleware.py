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
    Shows only TOP 2 urgent alerts + link to full page
    Uses session to prevent duplicates
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Only show notifications for admin users on admin pages
        if request.user.is_authenticated and request.user.is_staff and request.path.startswith('/znd/'):
            # Check if this is first visit to admin in this session
            if not request.session.get('admin_notifications_shown', False):
                self.show_top_notifications(request)
                # Mark as shown for this session
                request.session['admin_notifications_shown'] = True
        
        response = self.get_response(request)
        return response
    
    def show_top_notifications(self, request):
        """Show only the TOP 2 most urgent notifications + link to see all"""
        
        # Get today's date
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        urgent_count = 0
        
        # 1. CHECK OLD PENDING ORDERS (MOST URGENT)
        old_orders = Order.objects.filter(status='pending', created_at__date__lte=yesterday)
        old_count = old_orders.count()
        
        if old_count > 0:
            messages.error(
                request,
                mark_safe(
                    f"🚨 URGENT: {old_count} pending order(s) are more than 24 hours old! "
                    f'<a href="/znd/orders/order/?status__exact=pending" style="color: white; text-decoration: underline;">View Now</a>'
                )
            )
            urgent_count += 1
        
        # 2. CHECK FAILED SMS (SECOND MOST URGENT)
        if urgent_count < 2:
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
                urgent_count += 1
        
        # 3. If less than 2 urgent, show new pending orders
        if urgent_count < 2:
            new_pending = Order.objects.filter(status='pending', created_at__date=today).count()
            
            if new_pending > 0:
                messages.warning(
                    request,
                    mark_safe(
                        f"📦 You have {new_pending} new pending order(s) waiting to be processed. "
                        f'<a href="/znd/orders/order/?status__exact=pending" style="color: white; text-decoration: underline;">View Orders</a>'
                    )
                )
                urgent_count += 1
        
        # ALWAYS SHOW: Link to see all notifications
        total_notifications = self.count_all_notifications()
        
        if total_notifications > urgent_count:
            remaining = total_notifications - urgent_count
            messages.info(
                request,
                mark_safe(
                    f"🔔 You have {remaining} more notification(s). "
                    f'<a href="/znd/notifications/" style="color: white; text-decoration: underline; font-weight: bold;">See All Notifications</a>'
                )
            )
    
    def count_all_notifications(self):
        """Count total number of notifications"""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        count = 0
        
        # Old pending orders
        count += Order.objects.filter(status='pending', created_at__date__lte=yesterday).count()
        
        # New pending orders
        if Order.objects.filter(status='pending', created_at__date=today).exists():
            count += 1
        
        # Unread messages (today)
        if Contact.objects.filter(is_read=False, created_at__date=today).exists():
            count += 1
        
        # Unread messages (older)
        if Contact.objects.filter(is_read=False, created_at__date__lt=today).exists():
            count += 1
        
        # Wishlist items today
        if Wishlist.objects.filter(added_date__date=today).exists():
            count += 1
        
        # Failed SMS
        from users.models import SMSMessage
        count += SMSMessage.objects.filter(status='failed').count()
        
        return count