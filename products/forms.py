from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'quantity', 'price', 'description', 'picture', 'picture_2', 'picture_3']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'picture': forms.FileInput(attrs={'class': 'form-control'}),
            'picture_2': forms.FileInput(attrs={'class': 'form-control'}),
            'picture_3': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'picture': 'Main Image',
            'picture_2': 'Second Image (Optional)',
            'picture_3': 'Third Image (Optional)',
        }