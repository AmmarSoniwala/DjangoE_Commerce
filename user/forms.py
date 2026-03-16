from django import forms
from accounts.models import Address
from products.models import ProductReview

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['label', 'apartment_number', 'street_line_1', 'street_line_2', 'city', 'state', 'postal_code', 'is_default']
        widgets = {
            'label': forms.Select(attrs={'class': 'form-select', 'style': 'margin-left: 10px; height: 60px;'}),
            'apartment_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apartment'}),
            'street_line_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address'}),
            'street_line_2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['comment', 'stars']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Comment'}),
            'stars': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stars'})
        }
