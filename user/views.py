from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from accounts.models import User, Address
from products.models import Products, ProductReview
from services.auth import get_user, is_admin
from django.contrib import messages
from .models import Cart, CartItem
from services.db import get_product, check_cart, check_cart_item, get_product_comments
from .forms import AddressForm, CommentForm

def HomeView(request):
    user = get_user(request)
    is_superuser = False
    cart_items = {}
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
    category = request.GET.get('category')

    if isinstance(user, HttpResponseRedirect):
        return user
    if user:
        is_superuser = is_admin(user.email)
    
    if category:
        product_list = Products.objects.filter(category=category)
    else:
        product_list = Products.objects.all()

    paginator = Paginator(product_list, 10)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    cart = check_cart(user=user)
    if cart:
        for product in products:
            cart_prod = check_cart_item(user=user, prod_id=product.id)
            if cart_prod:
                cart_items[f"{product.id}"] = cart_prod.quantity
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
        prod_dict = {
            "id": product.id,
            "name": product.name,
            "brand": product.brand,
            "price": product.price,
            "image": product.image.url,
            "discount": product.discount,
            "is_discounted": product.is_discounted,
            "category": product.category,
            "description": product.description,
            "stock": product.stock,
            "comments": None
        }
        if product.is_discounted > 0:
            prod_dict["discounted_price"] = product.discounted_price
        
        comment_dict = {}

        comments = get_product_comments(product)
        if comments:
            for comment in comments[:5]:
                comment_dict[comment.id] = {
                    "comment_id": comment.id,
                    "comment_user": comment.user,
                    "comment_text": comment.comment,
                    "comment_stars": comment.stars,
                    "comment_created_at": comment.created_at
                }
            prod_dict["comments"] = comment_dict

        context = {
            "product": prod_dict,
            "is_superuser": is_superuser,
            "user": user,
            "cart_item_quantity": cart_item_quantity
        }
        print("Context: ", context)
        return render(request, "user/product_detail.html", context=context)
    else:
        messages.warning(request, "Product not found")
        return redirect("home")

def AddressView(request):
    user = get_user(request)
    if isinstance(user, HttpResponseRedirect):
        return user
    if user:
        addresses = Address.objects.filter(user=user)
        address_list = []
        for address in addresses:
            address_list.append({
                "id": address.id,
                "label": address.get_label_display(),
                "street_line_1": address.street_line_1,
                "street_line_2": address.street_line_2,
                "apartment_number": address.apartment_number,
                "city": address.city,
                "state": address.state,
                "postal_code": address.postal_code,
                "is_default": address.is_default
            })
        context = {
            "addresses": address_list,
            "user": user,
            "total_address": addresses.count()
        }
        return render(request, "user/address.html", context=context)
    else:
        messages.warning(request, "User not found")
        return redirect("login")

def add_address(request):
    user = get_user(request)
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = user

            if address.is_default or not Address.objects.filter(user=user).exists():
                Address.objects.filter(user=user).update(is_default=False)
                address.is_default = True

            address.save()
            messages.success(request, "Address added successfully.")
            return redirect("address")
    else:
        form = AddressForm()
    return render(request, "user/add_address.html", {"form": form})


def edit_address(request, id):
    user = get_user(request)
    try:
        address = Address.objects.get(id=id, user=user)
    except Address.DoesNotExist:
        messages.error(request, "Address not found.")
        return redirect("address")

    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            address = form.save(commit=False)
            if address.is_default:
                Address.objects.filter(user=user).exclude(id=address.id).update(is_default=False)
            address.save()
            messages.success(request, "Address updated successfully.")
            return redirect("address")
    else:
        form = AddressForm(instance=address)
    
    return render(request, "user/add_address.html", {"form": form, "edit_mode": True})

def delete_address(request, id):
    user = get_user(request)
    try:
        address = Address.objects.get(id=id, user=user)
        address.delete()
        messages.success(request, "Address deleted successfully.")
    except Address.DoesNotExist:
        messages.error(request, "Address not found.")
        
    return redirect("address")

def add_comment(request, id):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = get_user(request)
            comment.product = get_product(id=id)
            comment.save()
            messages.success(request, "Comment added successfully.")
            return redirect("product_detail", id=id)
        else:
            messages.error(request, "Problem saving Comment!!")
            return redirect("product_detail", id=id)
    else:
        form = CommentForm()
        product = get_product(id=id)
        print("Product: ", product)
        comments = get_product_comments(product)
        print("Comments: ", comments)
        comment_dict = {}
        if comments:
            for comment in comments:
                comment_dict[comment.id] = {
                    "comment_id": comment.id,
                    "comment_user": comment.user,
                    "comment_text": comment.comment,
                    "comment_stars": comment.stars,
                    "comment_created_at": comment.created_at
                }
        print("Comment Dict: ", comment_dict)
        context = {
            "form": form,
            "product": product,
            "comments": comment_dict
        }
        return render(request, "user/add_comment.html", context=context)