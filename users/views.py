from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, Wishlist
from products.models import Product
from orders.models import Order
from django.contrib.auth.models import User
from django.db.models import Sum
from twilio.rest import Client
import random
from django.conf import settings
import logging
logger = logging.getLogger(__name__)

def clean_phone_number(phone):
    """Convert Algerian phone to +213XXXXXXXXX format"""
    phone = str(phone).replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    if phone.startswith('00213'):
        phone = '+' + phone[2:]
    elif phone.startswith('0'):
        phone = '+213' + phone[1:]
    elif phone.startswith('213'):
        phone = '+' + phone
    elif not phone.startswith('+'):
        phone = '+213' + phone
    
    return phone

def send_verification_sms(phone, code):
    """Send SMS verification code"""
    try:
        # Check if we have API Key credentials
        if hasattr(settings, 'SMS_API_KEY_SID') and settings.SMS_API_KEY_SID:
            # Using API Key (more secure)
            client = Client(
                settings.SMS_API_KEY_SID,
                settings.SMS_API_KEY_SECRET,
                settings.SMS_ACCOUNT_SID
            )
            logger.info("Using Twilio API Key authentication")
        else:
            # Using Auth Token
            client = Client(
                settings.SMS_ACCOUNT_SID,
                settings.SMS_AUTH_TOKEN
            )
            logger.info("Using Twilio Auth Token authentication")
        
        # Clean phone number
        phone = clean_phone_number(phone)
        logger.info(f"Sending SMS to: {phone}")
        
        # Send message
        message = client.messages.create(
            body=f"Your Bee House verification code is: {code} 🐝",
            from_=settings.SMS_TWILIO_NUMBER,
            to=phone
        )
        
        logger.info(f"SMS feels successfully. SID: {message.sid}")
        return True
        
    except Exception as e:
        logger.error(f"SMS Error: {str(e)}")
        logger.error(f"Phone number: {phone}")
        logger.error(f"Twilio Number: {settings.SMS_TWILIO_NUMBER}")
        raise e

def verify(request):
    reg_data = request.session.get('reg_data')
    if not reg_data:
        messages.error(request, 'Registration session expired. Please register again.')
        return redirect('users:register')

    if request.method == 'POST':
        user_input_code = request.POST.get('code')
        
        if user_input_code == reg_data['verification_code']:
            try:
                # Create the actual user now
                user = User.objects.create_user(
                    username=reg_data['username'],
                    password=reg_data['password'],
                    first_name=reg_data['first_name'],
                    last_name=reg_data['last_name']
                )
                UserProfile.objects.create(
                    user=user,
                    phone=reg_data['phone'],
                    address=reg_data['address']
                )
                del request.session['reg_data']  # Clear session
                messages.success(request, 'Account verified successfully! You can now login.')
                return redirect('users:login')
            except Exception as e:
                logger.error(f"Error creating user: {str(e)}")
                messages.error(request, 'Error creating account. Please try again.')
        else:
            messages.error(request, 'Invalid verification code. Please try again.')

    return render(request, 'users/verify.html', {'phone': reg_data.get('phone', '')})

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match!')
            return redirect('users:register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('users:register')

        # Generate verification code
        verification_code = str(random.randint(100000, 999999))
        
        # Save data in session temporarily
        request.session['reg_data'] = {
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'address': address,
            'password': password1,
            'verification_code': verification_code
        }

        # Try to send SMS
        try:
            send_verification_sms(phone, verification_code)
            messages.success(request, f'Verification code sent to {phone}!')
            return redirect('users:verify')
        except Exception as e:
            logger.error(f"Registration SMS failed: {str(e)}")
            
            return redirect('users:register')
        
    return render(request, 'users/register.html')

# Login View
def user_login(request):
    if request.user.is_authenticated:
        return redirect('home:home_page')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            
            # Redirect to next page or home
            next_page = request.GET.get('next', 'home:home_page')
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password!')
    
    return render(request, 'users/login.html')

# Logout View
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home:home_page')
# Profile
@login_required
def profile(request):
    if request.user.is_superuser:
        return redirect('/znd/')
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get statistics
    from orders.models import Order
    total_orders = Order.objects.filter(user=request.user).count()
    pending_orders = Order.objects.filter(user=request.user, status='pending').count()
    total_spent = Order.objects.filter(user=request.user).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Get recent orders
    recent_orders = Order.objects.filter(user=request.user).prefetch_related('items')[:5]
    
    # Get wishlist items
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    if request.method == 'POST':
        # Update profile
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()
        
        profile.phone = request.POST.get('phone')
        profile.address = request.POST.get('address')
        
        if request.FILES.get('profile_picture'):
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('users:profile')
    
    context = {
        'profile': profile,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_spent': total_spent,
        'recent_orders': recent_orders,
        'wishlist_items': wishlist_items,
    }
    
    return render(request, 'users/profilepage.html', context)
@login_required
def add_to_wishlist(request, product_id):
    """Add a product to user's wishlist"""
    product = get_object_or_404(Product, id=product_id)
    
    # Try to create wishlist item (will fail if already exists due to unique_together)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        messages.success(request, f'"{product.name}" added to your wishlist! ❤️')
    else:
        messages.info(request, f'"{product.name}" is already in your wishlist!')
    
    # Redirect to profile page with wishlist section
    return redirect('users:profile')


@login_required
def remove_from_wishlist(request, wishlist_id):
    """Remove a product from user's wishlist"""
    wishlist_item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    product_name = wishlist_item.product.name
    wishlist_item.delete()
    
    messages.success(request, f'"{product_name}" removed from your wishlist.')

    return redirect('users:profile')
