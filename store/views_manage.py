from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Product
from .forms import ProductForm

@staff_member_required
def manage_product_list(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'manage/product_list.html', {'products': products})

@staff_member_required
def manage_product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created')
            return redirect('manage_product_list')
    else:
        form = ProductForm()
    return render(request, 'manage/product_form.html', {'form': form, 'title': 'Add Product'})

@staff_member_required
def manage_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated')
            return redirect('manage_product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'manage/product_form.html', {'form': form, 'title': 'Edit Product'})

@staff_member_required
def manage_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted')
        return redirect('manage_product_list')
    return render(request, 'manage/product_confirm_delete.html', {'product': product})
