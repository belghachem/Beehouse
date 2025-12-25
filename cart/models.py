from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.db.models import Sum, F

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Cart - {self.user.username}"
    
    def get_total(self):
        total = self.items.aggregate(
            total=Sum(F('quantity') * F('product__price'))
        )['total']
        return total 

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    def get_total_price(self):
        return self.quantity * self.product.price
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"