from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from products.models import Product
from .cart import Cart
from .forms import CartAddProductForm
from django.conf import settings
from decimal import Decimal


def cart_detail(request):
    """Display cart contents"""
    cart = Cart(request)
    
    # Calculate totals
    subtotal = sum(Decimal(str(item['price'])) * item['quantity'] for item in cart)
    
    # Convert shipping to Decimal for calculation
    shipping = Decimal(str(settings.SHIPPING_COST))
    
    # Check if eligible for free shipping
    if subtotal >= Decimal(str(settings.FREE_SHIPPING_THRESHOLD)):
        shipping = Decimal('0.00')
    
    # Calculate VAT and total
    vat = (subtotal + shipping) * Decimal(str(settings.VAT_RATE))
    total = subtotal + shipping + vat
    
    context = {
        'cart': cart,
        'subtotal': subtotal,
        'shipping': shipping,
        'vat': vat,
        'total': total,
    }
    
    return render(request, 'cart/cart_detail.html', context)


@require_POST
def cart_add(request, product_id):
    """Add a product to the cart"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product,
            size=cd['size'],
            quantity=cd['quantity'],
            override_quantity=cd['override']
        )
        messages.success(request, f'{product.name} added to your cart!')
    else:
        messages.error(request, 'Please select a valid size and quantity.')
    
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    """Remove a product from the cart"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    size = request.POST.get('size')
    
    cart.remove(product, size)
    messages.success(request, f'{product.name} removed from your cart.')
    
    return redirect('cart:cart_detail')


def cart_clear(request):
    """Clear the entire cart"""
    cart = Cart(request)
    cart.clear()
    messages.success(request, 'Your cart has been cleared.')
    
    return redirect('cart:cart_detail')