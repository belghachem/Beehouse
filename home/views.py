from django.shortcuts import render
from products.models import Product  # Import products

def home_page(request):
    return render(request, 'home/index.html')