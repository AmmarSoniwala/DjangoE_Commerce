from django.db import models
from accounts.models import User

class CategoryChoices(models.TextChoices):
    ELECTRONICS = "Electronics", "Electronics & Gadgets"
    CLOTHING = "Clothing", "Summer & Winter Clothing"
    SHOES = "Shoes", "Footwear"
    GROCERY = "Grocery", "Grocery & Staples"
    BEAUTY = "Beauty", "Beauty & Health"
    HOME = "Home", "Home & Garden"
    OTHER = "Other", "Other"

class Products(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=20)
    price = models.IntegerField()
    discount = models.IntegerField(default=0)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CategoryChoices.choices, default=CategoryChoices.OTHER)
    image = models.ImageField(upload_to='image/', null=True, blank=True)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    @property
    def is_discounted(self):
        return self.discount > 0

    @property
    def discounted_price(self):
        if self.is_discounted:
            return round(self.price * (1 - self.discount / 100))
        return self.price

class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    stars = models.IntegerField(
        choices=(
            (1, '1'),
            (2, '2'),
            (3, '3'),
            (4, '4'),
            (5, '5'),
        )
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name