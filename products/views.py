from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ProductForm
from .models import Products
from services.auth import is_admin, authenticated, get_user

def add_product(request):
    if request.method == 'POST':
        # request.FILES must be passed to handle the image upload
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect('add_product')
        else:
            messages.warning(request, "Problem adding the Product")
            return redirect('add_product')
    else:
        user = get_user(request=request)
        validate = is_admin(user.email)
        if user and validate:
            form = ProductForm()
            return render(request, 'products/add_product.html', {'form': form})
        else:
            return redirect("home")

def update(request):
    user = get_user(request=request)
    validate = is_admin(user.email)
    if user and validate:
        dict = {}
        products = Products.objects.all()
        for idx, product in enumerate(products):
            dict[f"product_{idx}"] = {'id': product.id, 'image': product.image, 'name': product.name, 'brand': product.brand}
        return render(request, 'products/update_page.html', {'dict': dict})
    else:
        return redirect("home")

def update_product(request, id):
    if request.method == 'POST':
        product = Products.objects.get(id=id)
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product Update Successfully!!")
            return redirect('update_page')
        else:
            messages.warning(request, "Problem updating the product!!")
            return redirect('update_page')
    else:
        user = get_user(request=request)
        validate = is_admin(user.email)
        if user and validate:
            product = Products.objects.get(id=id)
            form = ProductForm(instance=product)
            return render(request, 'products/update_product.html', {'form': form})
        else:
            return redirect("home")

def delete_product(request, id):
    user = get_user(request=request)
    validate = is_admin(user.email)
    if user and validate:
        if request.method == 'POST':
            product = Products.objects.get(id=id)
            product.delete()
            messages.success(request, "Product deleted successfully!")
        return redirect('update_page')
    else:
        return redirect("home")
