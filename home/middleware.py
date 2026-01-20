from .models import Visitor


class VisitorTrackingMiddleware:
    """Middleware to track all website visitors"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Get visitor information
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        page_visited = request.path
        referrer = request.META.get('HTTP_REFERER', '')
        
        # Get or create session key
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        
        # Skip tracking for admin, static, and media files
        if not any(page_visited.startswith(path) for path in ['/znd/', '/static/', '/media/']):
            # Create visitor record
            Visitor.objects.create(
                ip_address=ip_address,
                user_agent=user_agent,
                page_visited=page_visited,
                referrer=referrer,
                session_key=session_key
            )
        
        response = self.get_response(request)
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip