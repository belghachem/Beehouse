from django.shortcuts import render, get_object_or_404
from django.db.models import F
from .models import Product

def prodects_page(request):
    products = Product.objects.all()  # Get all products from database
    return render(request, 'products/prodect_page.html', {
        'products': products
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    Product.objects.filter(slug=slug).update(view_count= F('view_count') + 1)
    product.refresh_from_db()
    return render(request, 'products/product_detail.html', {'product': product})
