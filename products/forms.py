from django import forms
from .models import Products

class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['image', 'name', 'brand', 'stock', 'price', 'discount', 'category', 'description']
        
        # Adding some basic Bootstrap styling classes to the widgets
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brand Name'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'min': '0'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'min': '0', 'step': '10'}),
            'discount': forms.HiddenInput(attrs={'id': 'id_discount'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Product Description...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        
        # Check if an image was uploaded (it's optional in the model)
        if image:
            # Use 'and' or wrap an 'or', because a file cannot be both .jpg AND .png
            if not (str(image.name).lower().endswith('.jpg') or str(image.name).lower().endswith('.png')):
                raise forms.ValidationError("Image must be a .jpg or .png file")
                
        price = cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError("Price cannot be negative")
            
        stock = cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError("Stock cannot be negative")

        discount = cleaned_data.get('discount')
        if discount is not None and (discount < 0 or discount > 100):
            raise forms.ValidationError("Discount cannot be less than 0 or greater than 100")
            
        return cleaned_data