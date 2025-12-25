from django.db import models

class Contact(models.Model):
    SUBJECT_CHOICES = [
        ('product', 'Product Inquiry'),
        ('order', 'Order Status'),
        ('wholesale', 'Wholesale Inquiry'),
        ('feedback', 'Feedback'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"