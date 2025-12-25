from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Contact

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')
        
        if not name or not phone or not subject or not message_text:
            messages.error(request, 'Please fill in all required fields!')
            return redirect('contactus:contact')
        
        try:
            Contact.objects.create(
                name=name,
                phone=phone,
                subject=subject,
                message=message_text
            )
            messages.success(request, f'Thank you {name}! Your message has been sent successfully. We will get back to you soon! 🐝')
            return redirect('contactus:contact')
        
        except Exception as e:
            print(f"Error saving contact: {e}")  # Debug print
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect('contactus:contact')
    
    return render(request, 'contactus/contactus.html')