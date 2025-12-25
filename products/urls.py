from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.prodects_page, name='product_page'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]