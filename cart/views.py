from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from products.models import Product
from .models import Cart, CartItem

@login_required
def add_to_cart(request, product_id):
    """Add product to cart - AJAX enabled"""
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    # Check if AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_count = sum(item.quantity for item in cart.items.all())
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart!',
            'cart_count': cart_count,
            'cart_total': float(cart.get_total())
        })
    
    # Fallback for non-AJAX
    return redirect('cart:view_cart')

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    total = sum(item.get_total_price() for item in cart_items)
    
    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart:view_cart')

@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    
    return redirect('cart:view_cart')

@login_required
def get_cart_count(request):
    """API endpoint to get cart count"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_count = sum(item.quantity for item in cart.items.all())
    return JsonResponse({'cart_count': cart_count})