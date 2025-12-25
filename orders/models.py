from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.core.cache import cache

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    DELIVERY_CHOICES = [
        ('home', 'Home Delivery'),
        ('stop_desk', 'Stop Desk (Point de Retrait)'),
    ]

    stop_desk = models.ForeignKey(
        'StopDesk', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Selected stop desk for pickup"
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, default='cod', editable=False)
    
    # Prices
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, help_text="Product total")
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Subtotal + Shipping")
    
    # Shipping Info
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    wilaya = models.CharField(max_length=100)
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='home')
    
    # Map coordinates
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Tracking
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['wilaya', 'delivery_type']),
        ]
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"
    
    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    def calculate_shipping(self):
        """Calculate shipping cost based on wilaya and delivery type"""
        return ShippingRate.get_shipping_cost(self.wilaya, self.delivery_type)

class ShippingRate(models.Model):
    wilaya = models.CharField(max_length=100, unique=True)
    home_delivery_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Prix Unitaire H.T.")
    stop_desk_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Stop Desk price")
    return_cost = models.DecimalField(max_digits=10, decimal_places=2, default=300.00)
    
    class Meta:
        ordering = ['wilaya']
        verbose_name = "Shipping Rate"
        verbose_name_plural = "Shipping Rates"
    
    def __str__(self):
        return f"{self.wilaya} - {self.home_delivery_price} DA"

    @classmethod
    def get_shipping_cost(cls, wilaya, delivery_type='home'):
        cache_key = f'shipping_{wilaya}_{delivery_type}'
        cost = cache.get(cache_key)
        
        if cost is None:
            try:
                spleen = cls.objects.get(wilaya=wilaya)
                cost = spleen.stop_desk_price if delivery_type == 'stop_desk' else spleen.home_delivery_price
                cache.set(cache_key, cost, 3600)  # Cache for 1 hour
            except cls.DoesNotExist:
                cost = 400.00
        
        return cost


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def get_total_price(self):
        """Calculate total price safely"""
        try:
            quantity = self.quantity if self.quantity is not None else 0
            price = self.price if self.price is not None else 0
            return quantity * price
        except:
            return 0
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

class StopDesk(models.Model):
    """Stop Desk / Point de Retrait locations"""
    name = models.CharField(max_length=200, help_text="Stop Desk name")
    wilaya = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    
    # Working hours
    working_hours = models.CharField(max_length=100, default="08:00 - 18:00", help_text="e.g., 08:00 - 18:00")
    working_days = models.CharField(max_length=100, default="Sunday - Thursday", help_text="e.g., Sunday - Thursday")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['wilaya', 'city', 'name']
        verbose_name = "Stop Desk"
        verbose_name_plural = "Stop Desks"
    
    def __str__(self):
        return f"{self.name} - {self.city}, {self.wilaya}"
    
    @classmethod
    def get_by_wilaya(cls, wilaya):
        """Get all active stop desks in a wilaya"""
        return cls.objects.filter(wilaya=wilaya, is_active=True)