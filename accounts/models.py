from django.db import models

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=15)
    refresh_token = models.CharField(max_length=255, blank=True, null=True)
    super_user = models.BooleanField(default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Address(models.Model):
    ADDRESS_TYPES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=20, choices=ADDRESS_TYPES, default='home')
    apartment_number = models.CharField(max_length=20, blank=True)
    street_line_1 = models.CharField(max_length=100)
    street_line_2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.label} - {self.street_line_1}, {self.city}"

    class Meta:
        verbose_name_plural = "Addresses"

class OTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user.phone_number} - {self.otp}"