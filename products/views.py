from django.shortcuts import render, get_object_or_404
from .models import Product

def prodects_page(request):  # Fixed typo
    products = Product.objects.all()  # Get all products from database
    return render(request, 'products/prodect_page.html', {
        'products': products
    })
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'products/product_detail.html', {'product': product})