from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order, OrderItem
from django.urls import reverse
from decimal import Decimal
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST


def home(request):
    products = Product.objects.filter(status='ACTIVE')
    return render(request, 'home.html', {'products': products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST' and request.headers.get('x-requested-with') != 'XMLHttpRequest':
        # non-AJAX fallback (redirect)
        qty = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        cart_item = cart.get(str(product.product_id), {'qty': 0, 'name': product.name, 'price': str(product.price), 'image_url': product.image_url or ''})
        cart_item['qty'] += qty
        cart_item['image_url'] = product.image_url or ''
        cart[str(product.product_id)] = cart_item
        request.session['cart'] = cart
        return redirect('cart')
    return render(request, 'product_detail.html', {'product': product})


def cart_view(request):
    """Render the cart page (kept as a regular view for /cart/)."""
    cart = request.session.get('cart', {})
    items = []
    total = Decimal('0.00')
    for pid, data in cart.items():
        subtotal = Decimal(data['price']) * data['qty']
        items.append({'product_id': pid, 'name': data['name'], 'qty': data['qty'], 'price': data['price'], 'subtotal': subtotal, 'image_url': data.get('image_url', '')})
        total += subtotal
    return render(request, 'cart.html', {'items': items, 'total': total})


def cart_update(request, pid):
    """Non-AJAX fallback to update or remove an item in the cart and redirect to cart page."""
    if request.method != 'POST':
        return redirect('cart')
    cart = request.session.get('cart', {})
    action = request.POST.get('action')
    if action == 'remove':
        cart.pop(pid, None)
    else:
        try:
            qty = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            qty = 1
        if qty <= 0:
            cart.pop(pid, None)
        else:
            if pid in cart:
                cart[pid]['qty'] = qty
    request.session['cart'] = cart
    return redirect('cart')

@require_POST
def add_to_cart_ajax(request, pk):
    product = get_object_or_404(Product, pk=pk)
    try:
        qty = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        return HttpResponseBadRequest('Invalid quantity')
    cart = request.session.get('cart', {})
    pid = str(product.product_id)
    item = cart.get(pid, {'qty': 0, 'name': product.name, 'price': str(product.price), 'image_url': product.image_url or ''})
    item['qty'] += qty
    item['image_url'] = product.image_url or ''
    cart[pid] = item
    request.session['cart'] = cart
    total_count = sum(v['qty'] for v in cart.values())
    return JsonResponse({'success': True, 'cart_count': total_count, 'item_qty': cart[pid]['qty']})


@require_POST
def cart_update_ajax(request):
    pid = request.POST.get('pid')
    if not pid:
        return HttpResponseBadRequest('Missing pid')
    cart = request.session.get('cart', {})
    if pid not in cart:
        return HttpResponseBadRequest('Item not in cart')
    action = request.POST.get('action')
    if action == 'remove':
        cart.pop(pid, None)
        request.session['cart'] = cart
        total_count = sum(v['qty'] for v in cart.values())
        total_amount = sum(Decimal(v['price']) * v['qty'] for v in cart.values())
        return JsonResponse({'success': True, 'removed': True, 'cart_count': total_count, 'total_amount': str(total_amount)})
    try:
        qty = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        return HttpResponseBadRequest('Invalid quantity')
    if qty <= 0:
        cart.pop(pid, None)
    else:
        cart[pid]['qty'] = qty
    request.session['cart'] = cart
    item_subtotal = Decimal(cart[pid]['price']) * cart[pid]['qty'] if pid in cart else Decimal('0.00')
    total_count = sum(v['qty'] for v in cart.values())
    total_amount = sum(Decimal(v['price']) * v['qty'] for v in cart.values())
    return JsonResponse({'success': True, 'cart_count': total_count, 'item_subtotal': str(item_subtotal), 'total_amount': str(total_amount)})


def cart_summary_ajax(request):
    cart = request.session.get('cart', {})
    total_count = sum(v['qty'] for v in cart.values())
    total_amount = sum(Decimal(v['price']) * v['qty'] for v in cart.values())
    return JsonResponse({'cart_count': total_count, 'total_amount': str(total_amount)})


@require_POST
def checkout_prepare(request):
    # Expects 'selected' as comma-separated pids or multiple form fields
    selected = request.POST.getlist('selected') or request.POST.get('selected')
    if isinstance(selected, str):
        selected = [s for s in selected.split(',') if s]
    selected = [str(s) for s in selected if s]
    if not selected:
        return JsonResponse({'success': False, 'error': 'no_items_selected'})
    # ensure they exist in cart
    cart = request.session.get('cart', {})
    selected_existing = [pid for pid in selected if pid in cart]
    if not selected_existing:
        return JsonResponse({'success': False, 'error': 'no_items_in_cart'})
    request.session['selected_for_checkout'] = selected_existing
    return JsonResponse({'success': True, 'redirect': reverse('checkout')})


def checkout(request):
    cart = request.session.get('cart', {})
    selected = request.session.get('selected_for_checkout', [])
    if not selected:
        # No items prepared for checkout
        from django.contrib import messages
        messages.warning(request, 'Please select at least one item to checkout.')
        return redirect('cart')
    # Filter cart to selected items
    selected_items = {pid: cart[pid] for pid in selected if pid in cart}
    if not selected_items:
        from django.contrib import messages
        messages.warning(request, 'Selected items are not in the cart.')
        return redirect('cart')
    items = []
    total = Decimal('0.00')
    for pid, data in selected_items.items():
        subtotal = Decimal(data['price']) * data['qty']
        items.append({'product_id': pid, 'name': data['name'], 'qty': data['qty'], 'price': data['price'], 'subtotal': subtotal, 'image_url': data.get('image_url', '')})
        total += subtotal

    if request.method == 'POST':
        # process order only for selected items
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        order = Order.objects.create(customer_name=name, customer_email=email, customer_phone=phone, shipping_address=address, total_amount=total)
        for pid, data in selected_items.items():
            product = Product.objects.get(product_id=int(pid))
            qty = data['qty']
            unit_price = Decimal(data['price'])
            subtotal = unit_price * qty
            OrderItem.objects.create(order=order, product=product, quantity=qty, unit_price=unit_price, subtotal=subtotal)
        # remove purchased items from cart
        for pid in selected_items:
            cart.pop(pid, None)
        request.session['cart'] = cart
        request.session.pop('selected_for_checkout', None)
        return redirect(reverse('order_confirmation', args=[order.order_id]))

    return render(request, 'checkout.html', {'items': items, 'total': total})


def order_confirmation(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    return render(request, 'order_confirmation.html', {'order': order})
