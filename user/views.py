from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from accounts.models import User
from products.models import Products
from services.auth import get_user, is_admin
from django.contrib import messages
from .models import Cart, CartItem
from services.db import get_product, check_cart, check_cart_item

def HomeView(request):
    user = get_user(request)
    is_superuser = False
    cart_items = {}
    if isinstance(user, HttpResponseRedirect):
        return user
    if user:
        is_superuser = is_admin(user.email)
        try:
            cart = Cart.objects.get(user=user)
            items = CartItem.objects.filter(cart=cart)
            cart_items = {item.product.id: item.quantity for item in items}
        except Cart.DoesNotExist:
            cart_items = {}
    
    products = Products.objects.all()
    elec_products = products.filter(category="Electronics")
    cloth_products = products.filter(category="Clothing")
    shoe_products = products.filter(category="Shoes")
    grocery_products = products.filter(category="Grocery")
    beauty_products = products.filter(category="Beauty")
    home_products = products.filter(category="Home")
    other_products = products.filter(category="Other")

    dict = {
        "elec_products": elec_products,
        "cloth_products": cloth_products,
        "shoe_products": shoe_products,
        "grocery_products": grocery_products,
        "beauty_products": beauty_products,
        "home_products": home_products,
        "other_products": other_products,
        "is_superuser": is_superuser,
        "user": user,
        "cart_items": cart_items
    }
    return render(request, "home.html", context=dict)

def CategoryView(request):
    user = get_user(request)
    is_superuser = False
    cart_items = {}
    if isinstance(user, HttpResponseRedirect):
        return user
    if user:
        is_superuser = is_admin(user.email)
    
    category = request.GET.get('category')
    if category:
        product_list = Products.objects.filter(category=category)
    else:
        product_list = Products.objects.all()

    paginator = Paginator(product_list, 10)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    cart = check_cart(user=user)
    if cart:
        for idx, product in enumerate(products):
            cart_prod = check_cart_item(user=user, prod_id=product.id)
            if cart_prod:
                cart_items[f"prod_{idx}"] = cart_prod.quantity
            else:
                continue
    else:
        messages.info(request, "Please login to add items to your cart")
        cart_items = {}

    context = {
        "products": products,
        "category": category,
        "is_superuser": is_superuser,
        "user": user,
        "cart_items": cart_items
    }
    print("Context: ", context)
    return render(request, "category.html", context=context)

def ProductView(request, id):
    user = get_user(request=request)
    is_superuser = False
    cart_item_quantity = 0
    if isinstance(user, HttpResponseRedirect):
        return user
    if user:
        is_superuser = is_admin(user.email)
        try:
            cart = check_cart(user=user)
            if cart:
                cart_item = check_cart_item(user=user, prod_id=id)
                if cart_item:
                    cart_item_quantity = cart_item.quantity
                else:
                    cart_item_quantity = 0
        except Cart.DoesNotExist:
            messages.warning(request, "Cart not found")
    else:
        messages.warning(request, "User not found")
        return redirect("home")
    
    product = get_product(id=id)
    if product:
        context = {
            "product": product,
            "is_superuser": is_superuser,
            "user": user,
            "cart_item_quantity": cart_item_quantity
        }
        return render(request, "product_detail.html", context=context)
    else:
        messages.warning(request, "Product not found")
        return redirect("home")