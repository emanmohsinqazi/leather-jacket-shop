from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'full_name', 'email', 'phone',
            'address_line_1', 'address_line_2',
            'city', 'county', 'postcode',
            'shipping_method',
            'payment_method'  # NEW!
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'John Smith'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'john@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+44 20 1234 5678'
            }),
            'address_line_1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '123 Main Street'
            }),
            'address_line_2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apartment, suite, etc. (optional)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'London'
            }),
            'county': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Greater London (optional)'
            }),
            'postcode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SW1A 1AA'
            }),
            'shipping_method': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            }),
            'payment_method': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone': 'Phone Number',
            'address_line_1': 'Address Line 1',
            'address_line_2': 'Address Line 2',
            'city': 'City',
            'county': 'County',
            'postcode': 'Postcode',
            'shipping_method': 'Shipping Method',
            'payment_method': 'Payment Method'
        }