from products.models import Products, ProductReview
from user.models import Cart, CartItem

def get_product(id):
    try:
        product = Products.objects.get(id=id)
        if product.stock < 1:
            return None
        return product
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
        if not cart:
            return None
        return CartItem.objects.filter(cart=cart, product=prod_id).first()
    except CartItem.DoesNotExist:
        return None

def create_cart(user):
    cart = Cart.objects.create(user=user) 
    return cart

def create_cart_item(cart, product, quantity=1):
    cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)
    return cart_item

def update_cart_item(cart_item, quantity=1):
    cart_item.quantity = quantity
    cart_item.save()
    return cart_item

def delete_cart_item(cart_item):
    cart_item.delete()
    return cart_item

def delete_cart(cart):
    cart.delete()
    return cart

def get_cart_items(cart):
    return CartItem.objects.filter(cart=cart)

def delete_cart_item_quantity(cart_item, quantity=1):
    try:
        cart_item.quantity-=quantity
        cart_item.save()
        if cart_item.quantity == 0:
            delete_cart_item(cart_item=cart_item)
            if get_cart_items(cart_item.cart).count() == 0:
                delete_cart(cart=cart_item.cart)
                return {"msg": "Cart is empty", "status": "success"}
            return {"msg": "Cart item deleted", "status": "success"}

        return {"msg": "Cart item quantity decrease by 1", "status": "success"}
    except CartItem.DoesNotExist:
        return {"msg": "Cart item not found", "status": "error"}

def get_item_detail(cart_item):
    product = cart_item.product
    discounted_price = product.discounted_price
    quantity = cart_item.quantity
    item_total = discounted_price * quantity

    return ({
        "id": cart_item.id,
        "product_id": product.id,
        "image": product.image,
        "name": product.name,
        "brand": product.brand,
        "price": product.price,
        "discount": product.discount,
        "is_discounted": product.is_discounted,
        "discounted_price": discounted_price,
        "quantity": quantity,
        "item_total": item_total,
    }, item_total)

def get_product_comments(product):
    try:
        comments = ProductReview.objects.filter(product=product)
        return comments
    except ProductReview.DoesNotExist:
        return None