from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('znd/', admin.site.urls),
    path('', include('home.urls')),                    # Home page
    path('products/', include('products.urls')),       # Products
    path('cart/', include('cart.urls')),               # Cart
    path('contact/', include('contactus.urls')),       # Contact
    path('users/', include('users.urls')),             # User profile
    path('orders/', include('orders.urls')),           # Orders
]

# Serve media files
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)