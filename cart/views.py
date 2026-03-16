from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from accounts.models import User
from services.auth import get_user
from services.db import (
    check_cart, check_cart_item, get_product, create_cart, create_cart_item,
    update_cart_item, delete_cart_item_quantity, delete_cart,
    get_cart_items, get_item_detail
)

def add_to_cart(request, prod_id):
    user = get_user(request)
    redirect_url = request.GET.get('redirect_url')
    product = get_product(id=prod_id)

    if not product:
        messages.error(request, "Product not found")
        return redirect('home')

    if not redirect_url:
        messages.error(request, "Redirect URL not found")
        return redirect('home')
    
    if isinstance(user, HttpResponseRedirect):
        return user
    
    if user:
        cart = check_cart(user=user)
        if not cart:
            cart = create_cart(user=user)
            create_cart_item(cart=cart, product=product)
            return redirect(redirect_url)
        else:
            cart_item = check_cart_item(user=user, prod_id=prod_id)
            if cart_item:
                update_cart_item(cart_item=cart_item, quantity=cart_item.quantity + 1)
                return redirect(redirect_url)
            else:
                create_cart_item(cart=cart, product=product)
                return redirect(redirect_url)
    
    return redirect('home')

def delete_to_cart(request, prod_id):
    user = get_user(request)
    redirect_url = request.GET.get('redirect_url')
    product = get_product(id=prod_id)
    
    if not product:
        messages.error(request, "Product not found")
        return redirect('home')
    if not redirect_url:
        messages.error(request, "Redirect URL not found")
        return redirect('home')
    if isinstance(user, HttpResponseRedirect):
        return user
    if user:
        cart = check_cart(user=user) 
        if not cart:
            messages.error(request, "Wrong Delete Request")
            return redirect('home')
        cart_item = check_cart_item(user=user, prod_id=prod_id)
        if cart_item:
            cart_item.delete()
            return redirect(redirect_url)
        messages.error(request, "Item not in cart")
    return redirect('home')

def delete_cart_item_1(request, prod_id):
    user = get_user(request)
    redirect_url = request.GET.get('redirect_url')
    product = get_product(id=prod_id)
    
    if not product:
        messages.error(request, "Product not found")
        return redirect('home')
    if not redirect_url:
        messages.error(request, "Redirect URL not found")
        return redirect('home')
    if isinstance(user, HttpResponseRedirect):
        return user
    if user:
        cart = check_cart(user=user) 
        if not cart:
            messages.error(request, "Wrong Delete Request")
            return redirect('home')
        cart_item = check_cart_item(user=user, prod_id=prod_id)
        if cart_item:
            delete_cart_item_quantity(cart_item=cart_item)
            return redirect(redirect_url)
        messages.error(request, "Item not in cart")
    return redirect('home')

def delete_user_cart(request):
    user = get_user(request)
    if isinstance(user, HttpResponseRedirect):
        return user
    if user:
        cart = check_cart(user=user)
        if cart:
            delete_cart(cart=cart)
    return redirect('home')

def CartView(request):
    user = get_user(request)

    if isinstance(user, HttpResponseRedirect):
        return user
    
    if user:
        cart = check_cart(user=user)
        if not cart:
            return render(request, 'cart.html', {"cart_items": [], "cart_total": 0})
        else:
            raw_items = get_cart_items(cart=cart)
            cart_items = []
            cart_total = 0
            for cart_item in raw_items:
                item_detail, item_total = get_item_detail(cart_item)
                cart_total += item_total
                cart_items.append(item_detail)
            context = {
                "cart_items": cart_items,
                "cart_total": cart_total,
            }
            return render(request, 'cart/cart.html', context)
    else:
        return redirect('home')
