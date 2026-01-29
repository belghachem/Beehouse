from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from cloudinary.models import CloudinaryField

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    wilaya = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_total_orders(self):
        return self.user.order_set.count()
    
    def get_pending_orders(self):
        return self.user.order_set.filter(status='pending').count()
    
    def get_total_spent(self):
        from django.db.models import Sum
        total = self.user.order_set.aggregate(Sum('total_price'))['total_price__sum']
        return total if total else 0

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-added_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


#FOR SMS
class SMSMessage(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    phone_number = models.CharField(max_length=20)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"SMS to {self.phone_number} - {self.status}"