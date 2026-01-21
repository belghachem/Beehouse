from django.db import models
from django.utils import timezone
from datetime import timedelta

class Visitor(models.Model):
    """Track website visitors"""
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    page_visited = models.CharField(max_length=500)
    referrer = models.CharField(max_length=500, blank=True, null=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)
    visited_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-visited_at']
        indexes = [
            models.Index(fields=['-visited_at']),
            models.Index(fields=['ip_address', 'visited_at']),
        ]
    
    def __str__(self):
        return f"{self.ip_address} - {self.visited_at.strftime('%Y-%m-%d %H:%M')}"
    
    @classmethod
    def get_today_count(cls):
        """Total visits today"""
        today = timezone.now().date()
        return cls.objects.filter(visited_at__date=today).count()
    
    @classmethod
    def get_today_unique_count(cls):
        """Unique visitors today"""
        today = timezone.now().date()
        return cls.objects.filter(
            visited_at__date=today
        ).values('ip_address').distinct().count()
    
    @classmethod
    def get_month_count(cls):
        """Total visits this month"""
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return cls.objects.filter(visited_at__gte=start_of_month).count()
    
    @classmethod
    def get_month_unique_count(cls):
        """Unique visitors this month"""
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return cls.objects.filter(
            visited_at__gte=start_of_month
        ).values('ip_address').distinct().count()
    
    @classmethod
    def get_last_n_days_data(cls, days=7):
        """Get visitor data for last N days"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        data = []
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            count = cls.objects.filter(visited_at__date=current_date).count()
            unique_count = cls.objects.filter(
                visited_at__date=current_date
            ).values('ip_address').distinct().count()
            
            data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'total': count,
                'unique': unique_count
            })
        
        return data
    
    @classmethod
    def get_popular_pages(cls, limit=10):
        """Get most visited pages"""
        from django.db.models import Count
        return cls.objects.values('page_visited').annotate(
            visit_count=Count('id')
        ).order_by('-visit_count')[:limit]
