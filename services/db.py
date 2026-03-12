from products.models import Products
from user.models import Cart, CartItem

def get_product(id):
    try:
        return Products.objects.get(id=id)
    except Products.DoesNotExist:
        return None
    
def check_cart(user):
    try:
        return Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        return None

def check_cart_item(user, prod_id):
    try:
        cart = check_cart(user)
        return CartItem.objects.filter(cart=cart, product=prod_id)
    except CartItem.DoesNotExist:
        return None