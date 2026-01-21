from django.db import models
from django.utils.text import slugify
from cloudinary.models import CloudinaryField

class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True) 
    category = models.CharField(max_length=100)
    quantity = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    picture =CloudinaryField('picture',blank=True, null=True)
    picture_2 = CloudinaryField('picture_2',blank=True, null=True)
    picture_3 =CloudinaryField('picture_3',blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at'] 
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['slug']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_images(self):
        """Return list of available product images"""
        images = []
        if self.picture:
            images.append(self.picture.url)
        if self.picture_2:
            images.append(self.picture_2.url)
        if self.picture_3:
            images.append(self.picture_3.url)

        return images if images else ['/static/Images/jarofhoney.jpg']

