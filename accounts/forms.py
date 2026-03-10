from django import forms
from .models import User, Address


class UserRegistrationForm(forms.ModelForm):
    """Form for registering a new User."""
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Hash the password before saving
        from django.contrib.auth.hashers import make_password
        user.password = make_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    """Form for logging in with full name (First Last) or email, plus password."""
    username_or_email = forms.CharField(
        label="Full Name or Email",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. John Doe  or  john@email.com'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput
    )

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username_or_email', '').strip()
        password = cleaned_data.get('password')

        user = None

        # Try matching by email first
        if '@' in username_or_email:
            try:
                user = User.objects.get(email=username_or_email)
            except User.DoesNotExist:
                raise forms.ValidationError("No account found with that email.")
        else:
            # Try matching by full name (first_name + " " + last_name)
            parts = username_or_email.split(' ', 1)
            if len(parts) == 2:
                first_name, last_name = parts
                try:
                    user = User.objects.get(first_name=first_name, last_name=last_name)
                except User.DoesNotExist:
                    raise forms.ValidationError("No account found with that name.")
            else:
                raise forms.ValidationError("Enter your full name (First Last) or email address.")

        # Verify the password
        from django.contrib.auth.hashers import check_password
        if user and not check_password(password, user.password):
            raise forms.ValidationError("Incorrect password.")

        # Store user so the view can access it
        self.user = user
        return cleaned_data


class UserUpdateForm(forms.ModelForm):

    """Form for updating an existing User's profile."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number']


class AddressForm(forms.ModelForm):
    """Form for adding or editing an Address."""

    class Meta:
        model = Address
        fields = [
            'label', 'apartment_number', 'street_line_1',
            'street_line_2', 'city', 'state', 'postal_code',
            'is_default',
        ]
        widgets = {
            'label': forms.Select(attrs={'class': 'form-control'}),
            'apartment_number': forms.TextInput(attrs={'placeholder': 'Apt / Flat No.'}),
            'street_line_1': forms.TextInput(attrs={'placeholder': 'Street Line 1'}),
            'street_line_2': forms.TextInput(attrs={'placeholder': 'Street Line 2 (optional)'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'placeholder': 'State'}),
            'postal_code': forms.TextInput(attrs={'placeholder': 'Postal Code'}),
        }
