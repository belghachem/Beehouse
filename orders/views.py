from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
import json
from .models import Order, OrderItem, StopDesk
from cart.models import Cart, CartItem
from users.models import UserProfile

@login_required
def checkout(request):
    """Display checkout page with user info pre-filled"""
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()
    
    if not cart_items:
        messages.warning(request, "Your cart is empty!")
        return redirect('cart:view_cart')
    
    # Get user profile if exists
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = None
    
    # Get all stop desks for map
    stop_desks = StopDesk.objects.filter(is_active=True)
    stop_desks_data = []
    for desk in stop_desks:
        stop_desks_data.append({
            'id': desk.id,
            'name': desk.name,
            'wilaya': desk.wilaya,
            'city': desk.city,
            'address': desk.address,
            'phone': desk.phone,
            'lat': float(desk.latitude),
            'lng': float(desk.longitude),
            'hours': desk.working_hours,
            'days': desk.working_days
        })
    
    total = cart.get_total()
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'profile': profile,
        'stop_desks_json': json.dumps(stop_desks_data)
    }
    
    return render(request, 'checkout.html', context)

@login_required
def place_order(request):
    """Process the order"""
    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.all()
        
        if not cart_items:
            messages.error(request, "Your cart is empty!")
            return redirect('cart:view_cart')
        
        # Get form data
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        wilaya = request.POST.get('wilaya')
        delivery_type = request.POST.get('delivery_type', 'home')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        shipping_cost = request.POST.get('shipping_cost', 800)
        stop_desk_id = request.POST.get('stop_desk_id')
        
        # Get stop desk if selected
        stop_desk = None
        if delivery_type == 'stop_desk' and stop_desk_id:
            try:
                stop_desk = StopDesk.objects.get(id=stop_desk_id)
            except StopDesk.DoesNotExist:
                pass
        
        # Calculate totals
        subtotal = cart.get_total()
        try:
            shipping_cost = int(shipping_cost)
        except:
            shipping_cost = 800.00
        
        total_price = subtotal + shipping_cost
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address=address,
            city=city,
            wilaya=wilaya,
            delivery_type=delivery_type,
            stop_desk=stop_desk,
            latitude=latitude if latitude else None,
            longitude=longitude if longitude else None,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            total_price=total_price,
            payment_method='cod'
        )
        
        # Create order items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
        
        # Clear cart
        cart_items.delete()
        
        messages.success(request, f"Order #{order.id} placed successfully!")
        return redirect('orders:order_confirmation', order_id=order.id)
    
    return redirect('orders:checkout')

@login_required
def order_confirmation(request, order_id):
    """Order confirmation page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'confirmation.html', {'order': order})

@login_required
def order_detail(request, order_id):
    """View single order details"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})

@login_required
def download_invoice(request, order_id):
    """Download invoice as HTML (can be printed to PDF by browser)"""
    # Allow admin users to see any invoice, regular users only their own
    if request.user.is_staff:
        order = get_object_or_404(Order, id=order_id)
    else:
        order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Render the invoice template
    html_content = render_to_string('invoice.html', {'order': order})
    
    # Return as downloadable HTML file
    response = HttpResponse(html_content, content_type='text/html')
    response['Content-Disposition'] = f'attachment; filename="invoice_order_{order.id}.html"'
    
    return response