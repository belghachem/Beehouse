from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, Wishlist, SMSMessage  
from products.models import Product
from orders.models import Order
from django.contrib.auth.models import User
from django.db.models import Sum
import random
from django.conf import settings
import logging
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from urllib.parse import urlparse

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
    """Send SMS - creates message in database, Android phone will send it"""
    try:
        # Clean phone number
        phone = clean_phone_number(phone)
        logger.info(f"Creating SMS for: {phone}")
        
        # Create SMS message in database
        sms = SMSMessage.objects.create(
            phone_number=phone,
            message=f"Your Bee House verification code is: {code} 🐝",
            status='pending'
        )
        
        logger.info(f"SMS queued successfully. ID: {sms.id}")
        return True
        
    except Exception as e:
        logger.error(f"SMS Error: {str(e)}")
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
                del request.session['reg_data']
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
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match!')
            return redirect('users:register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('users:register')

        verification_code = str(random.randint(100000, 999999))
        
        request.session['reg_data'] = {
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'address': address,
            'password': password1,
            'verification_code': verification_code
        }

        try:
            send_verification_sms(phone, verification_code)
            messages.success(request, f'Verification code sent to {phone}!')
            return redirect('users:verify')
        except Exception as e:
            logger.error(f"Registration SMS failed: {str(e)}")
            messages.error(request, f'Error sending SMS. Please try again.')
            return redirect('users:register')
        
    return render(request, 'users/register.html')

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
            
            # Try multiple sources for redirect URL in priority order:
            # 1. 'next' parameter from URL (from @login_required decorator)
            # 2. 'next' from POST data (from login form hidden field)
            # 3. Referer header (page user came from)
            # 4. Default to home page
            next_page = request.GET.get('next') or request.POST.get('next')
            
            if not next_page:
                # Get the referer (previous page)
                referer = request.META.get('HTTP_REFERER', '')
                # Only use referer if it's from our site and not the login page itself
                if referer and '/login' not in referer and request.get_host() in referer:
                    # Extract the path from the full URL
                    parsed = urlparse(referer)
                    next_page = parsed.path
                else:
                    next_page = 'home:home_page'
            
            # Security: ensure next_page doesn't redirect to external sites
            if next_page and (next_page.startswith('http://') or next_page.startswith('https://')):
                next_page = 'home:home_page'
            
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password!')
    
    return render(request, 'users/login.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home:home_page')

@login_required
def profile(request):
    if request.user.is_superuser:
        return redirect('/znd/')
    
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    from orders.models import Order
    total_orders = Order.objects.filter(user=request.user).count()
    pending_orders = Order.objects.filter(user=request.user, status='pending').count()
    total_spent = Order.objects.filter(user=request.user).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    recent_orders = Order.objects.filter(user=request.user).prefetch_related('items')[:5]
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    if request.method == 'POST':
        # Update user fields
        user = request.user
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.save()
        profile.phone = request.POST.get('phone', '').strip()
        profile.address = request.POST.get('address', '').strip()
        profile.city = request.POST.get('city', '').strip()
        profile.wilaya = request.POST.get('wilaya', '').strip()
        
        # Handle profile picture if uploaded
        if request.FILES.get('profile_picture'):
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()
        
        logger.info(f"Profile updated for user {user.username}: phone={profile.phone}, city={profile.city}, wilaya={profile.wilaya}")
        
        messages.success(request, 'Profile updated successfully! ✅')
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
    product = get_object_or_404(Product, id=product_id)
    
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        messages.success(request, f'"{product.name}" added to your wishlist! ❤️')
    else:
        messages.info(request, f'"{product.name}" is already in your wishlist!')
    
    return redirect('users:profile')

@login_required
def remove_from_wishlist(request, wishlist_id):
    wishlist_item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    product_name = wishlist_item.product.name
    wishlist_item.delete()
    
    messages.success(request, f'"{product_name}" removed from your wishlist.')
    return redirect('users:profile')

def forgot_password(request):
    if request.method == 'POST':
        username_or_phone = request.POST.get('username_or_phone')
        
        try:
            user = User.objects.get(username=username_or_phone)
        except User.DoesNotExist:
            try:
                profile = UserProfile.objects.get(phone=username_or_phone)
                user = profile.user
            except UserProfile.DoesNotExist:
                messages.error(request, 'No account found with that username or phone number.')
                return redirect('users:forgot_password')
        
        reset_code = str(random.randint(100000, 999999))
        
        request.session['reset_data'] = {
            'user_id': user.id,
            'reset_code': reset_code,
        }
        
        try:
            profile = UserProfile.objects.get(user=user)
            send_verification_sms(profile.phone, reset_code)
            messages.success(request, f'Password reset code sent to your phone!')
            return redirect('users:reset_password')
        except Exception as e:
            logger.error(f"Failed to send reset SMS: {str(e)}")
            messages.error(request, 'Error sending verification code. Please try again.')
            return redirect('users:forgot_password')
    
    return render(request, 'users/forgotten_password.html')

def reset_password(request):
    reset_data = request.session.get('reset_data')
    if not reset_data:
        messages.error(request, 'Password reset session expired. Please try again.')
        return redirect('users:forgot_password')
    
    if request.method == 'POST':
        code = request.POST.get('code')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        if code != reset_data['reset_code']:
            messages.error(request, 'Invalid verification code.')
            return render(request, 'users/reset_password.html')
        
        if new_password1 != new_password2:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'users/reset_password.html')
        
        try:
            user = User.objects.get(id=reset_data['user_id'])
            user.set_password(new_password1)
            user.save()
            
            del request.session['reset_data']
            
            messages.success(request, 'Password reset successfully! You can now login.')
            return redirect('users:login')
        except Exception as e:
            logger.error(f"Error resetting password: {str(e)}")
            messages.error(request, 'Error resetting password. Please try again.')
    
    return render(request, 'users/reset_password.html')


# ADD THESE NEW API VIEWS FOR ANDROID APP
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json

@csrf_exempt
@require_http_methods(["GET"])
def get_pending_sms(request):
    """API: Android app fetches pending SMS"""
    pending_messages = SMSMessage.objects.filter(status='pending').order_by('created_at')[:10]
    
    messages_data = []
    for msg in pending_messages:
        messages_data.append({
            'id': msg.id,
            'phone_number': msg.phone_number,
            'message': msg.message,
            'created_at': msg.created_at.isoformat(),
        })
    
    return JsonResponse({
        'status': 'success',
        'count': len(messages_data),
        'messages': messages_data
    })

@csrf_exempt
@require_http_methods(["POST"])
def update_sms_status(request):
    """API: Android app updates SMS status after sending"""
    try:
        data = json.loads(request.body)
        sms_id = data.get('id')
        status = data.get('status')
        error_message = data.get('error_message', '')
        
        sms = SMSMessage.objects.get(id=sms_id)
        sms.status = status
        if status == 'sent':
            sms.sent_at = timezone.now()
        if error_message:
            sms.error_message = error_message
        sms.save()
        
        return JsonResponse({'status': 'success', 'message': 'SMS status updated'})
    except SMSMessage.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'SMS not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def delete_sms(request):
    """API: Delete SMS after successful send"""
    try:
        data = json.loads(request.body)
        sms_id = data.get('id')
        
        sms = SMSMessage.objects.get(id=sms_id)
        sms.delete()
        
        return JsonResponse({
            'status': 'success', 
            'message': f'SMS #{sms_id} deleted successfully'
        })
    except SMSMessage.DoesNotExist:
        return JsonResponse({
            'status': 'error', 
            'message': 'SMS not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': str(e)
        }, status=400)