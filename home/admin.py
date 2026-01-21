from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from .models import Visitor
import json

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'page_visited', 'visited_at']
    list_filter = ['visited_at']
    search_fields = ['ip_address', 'page_visited']
    readonly_fields = ['ip_address', 'user_agent', 'page_visited', 'referrer', 'session_key', 'visited_at']
    date_hierarchy = 'visited_at'
    change_list_template = 'admin/visitor_changelist.html'
    # Read-only model
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    # Add custom dashboard URL
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='visitor_dashboard'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        """Dashboard with visitor statistics and charts"""
        
        # Get statistics
        today_total = Visitor.get_today_count()
        today_unique = Visitor.get_today_unique_count()
        month_total = Visitor.get_month_count()
        month_unique = Visitor.get_month_unique_count()
        
        # Get chart data
        last_7_days = Visitor.get_last_n_days_data(7)
        last_30_days = Visitor.get_last_n_days_data(30)
        popular_pages = Visitor.get_popular_pages(10)
        
        # Prepare chart data for JavaScript
        chart_data_7_days = {
            'labels': [item['date'] for item in last_7_days],
            'total': [item['total'] for item in last_7_days],
            'unique': [item['unique'] for item in last_7_days],
        }
        
        chart_data_30_days = {
            'labels': [item['date'] for item in last_30_days],
            'total': [item['total'] for item in last_30_days],
            'unique': [item['unique'] for item in last_30_days],
        }
        
        context = {
            'title': 'Visitor Statistics Dashboard',
            'site_header': admin.site.site_header,
            'site_title': admin.site.site_title,
            'today_total': today_total,
            'today_unique': today_unique,
            'month_total': month_total,
            'month_unique': month_unique,
            'popular_pages': popular_pages,
            'chart_data_7_days': json.dumps(chart_data_7_days),
            'chart_data_30_days': json.dumps(chart_data_30_days),
        }
        
        return render(request, 'admin/visitor_dashboard.html', context)


# Customize admin site
admin.site.site_header = "BeeHouse Admin"
admin.site.site_title = "BeeHouse Admin Portal"
admin.site.index_title = "Welcome to BeeHouse Administration"

