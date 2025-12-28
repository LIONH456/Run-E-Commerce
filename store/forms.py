from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image_url', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows':3}),
            'status': forms.Select(choices=[('ACTIVE','ACTIVE'), ('INACTIVE','INACTIVE')])
        }
