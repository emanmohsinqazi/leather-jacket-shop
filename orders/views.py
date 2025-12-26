from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from cart.cart import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm
from .emails import send_order_created_email, send_order_confirmed_email, send_order_shipped_email, send_order_delivered_email, send_order_cancelled_email
from decimal import Decimal
import stripe
import json

# Set up Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def get_shipping_cost(method, subtotal):
    """Calculate shipping cost based on method and subtotal"""
    shipping_costs = {
        'standard': Decimal('5.99'),
        'express': Decimal('9.99'),
        'next_day': Decimal('14.99'),
        'international': Decimal('24.99'),
    }
    
    # Free standard shipping over £50
    if method == 'standard' and subtotal >= Decimal(str(settings.FREE_SHIPPING_THRESHOLD)):
        return Decimal('0.00')
    
    return shipping_costs.get(method, Decimal('5.99'))


def get_estimated_delivery(method):
    """Get estimated delivery time for shipping method"""
    delivery_times = {
        'standard': '5-7 business days',
        'express': '2-3 business days',
        'next_day': 'Next business day',
        'international': '10-15 business days',
    }
    return delivery_times.get(method, '5-7 business days')


@login_required
def order_create(request):
    """Create a new order from cart contents"""
    cart = Cart(request)
    
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('products:product_list')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # Create order
            order = form.save(commit=False)
            order.user = request.user
            
            # Calculate totals
            subtotal = sum(Decimal(str(item['price'])) * item['quantity'] for item in cart)
            shipping_method = form.cleaned_data['shipping_method']
            shipping = get_shipping_cost(shipping_method, subtotal)
            
            vat = (subtotal + shipping) * Decimal(str(settings.VAT_RATE))
            total = subtotal + shipping + vat
            
            order.subtotal = subtotal
            order.shipping_cost = shipping
            order.vat = vat
            order.total_amount = total
            order.estimated_delivery = get_estimated_delivery(shipping_method)
            
            # Set payment amounts based on payment method
            payment_method = form.cleaned_data['payment_method']
            if payment_method == 'partial':
                # 50% now, 50% on delivery
                order.amount_paid_online = total / 2
                order.remaining_amount = total / 2
            else:
                # Full payment
                order.amount_paid_online = total
                order.remaining_amount = Decimal('0.00')
            
            order.save()
            
            # Create order items
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    size=item['size'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            # Send order created email
            try:
                send_order_created_email(order)
                messages.success(request, f'Order #{order.id} placed successfully! Check your email for confirmation.')
            except Exception as e:
                messages.success(request, f'Order #{order.id} placed successfully!')
                print(f"Email error: {e}")
            
            # Clear the cart
            cart.clear()
            
            # Always redirect to Stripe payment (for full or partial payment)
            return redirect('orders:payment', order_id=order.id)
    else:
        # Pre-fill form with user data if available
        initial_data = {
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        }
        form = OrderCreateForm(initial=initial_data)
    
    # Calculate preview totals for each shipping method
    subtotal = sum(Decimal(str(item['price'])) * item['quantity'] for item in cart)
    
    shipping_options = []
    for method, label in Order.SHIPPING_METHOD_CHOICES:
        shipping_cost = get_shipping_cost(method, subtotal)
        vat = (subtotal + shipping_cost) * Decimal(str(settings.VAT_RATE))
        total = subtotal + shipping_cost + vat
        delivery_time = get_estimated_delivery(method)
        
        shipping_options.append({
            'method': method,
            'label': label,
            'cost': shipping_cost,
            'delivery_time': delivery_time,
            'total': total,
        })
    
    context = {
        'cart': cart,
        'form': form,
        'subtotal': subtotal,
        'shipping_options': shipping_options,
    }
    
    return render(request, 'orders/order_create.html', context)


@login_required
def order_detail(request, order_id):
    """View details of a specific order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def order_list(request):
    """View all orders for the current user"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def payment(request, order_id):
    """Handle Stripe payment for an order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if order is already fully paid
    if order.paid:
        messages.info(request, 'This order has already been paid in full.')
        return redirect('orders:order_detail', order_id=order.id)
    
    # Check if partial payment already received
    if order.partial_payment_received and order.payment_method == 'partial':
        messages.info(request, f'Initial payment of £{order.amount_paid_online} received. Remaining £{order.remaining_amount} due on delivery.')
        return redirect('orders:order_detail', order_id=order.id)
    
    if request.method == 'POST':
        try:
            # Determine amount to charge
            if order.payment_method == 'partial':
                # Charge 50%
                amount_to_charge = order.amount_paid_online
            else:
                # Charge full amount
                amount_to_charge = order.total_amount
            
            # Create Stripe payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(amount_to_charge * 100),  # Convert to pence
                currency='gbp',
                metadata={
                    'order_id': order.id,
                    'user_id': order.user.id,
                    'payment_type': order.payment_method,
                }
            )
            
            order.stripe_payment_intent = intent.id
            order.save()
            
            return JsonResponse({
                'clientSecret': intent.client_secret
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    context = {
        'order': order,
        'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY,
        'payment_amount': order.amount_paid_online,
    }
    
    return render(request, 'orders/payment.html', context)


@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Handle payment success
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        order_id = payment_intent['metadata'].get('order_id')
        payment_type = payment_intent['metadata'].get('payment_type')
        
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                
                if payment_type == 'partial':
                    # Partial payment received
                    order.partial_payment_received = True
                    order.status = 'processing'
                else:
                    # Full payment received
                    order.paid = True
                    order.partial_payment_received = True
                    order.status = 'processing'
                
                order.save()
            except Order.DoesNotExist:
                pass
    
    return JsonResponse({'status': 'success'})


@login_required
def admin_order_list(request):
    """Admin view: List all orders"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    status_filter = request.GET.get('status', '')
    orders = Order.objects.all().select_related('user').prefetch_related('items__product')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    orders = orders.order_by('-created_at')
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
    }
    
    return render(request, 'admin/orders/admin_order_list.html', context)


@login_required
def admin_order_detail(request, order_id):
    """Admin view: View and update order details"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    order = get_object_or_404(Order.objects.select_related('user').prefetch_related('items__product'), id=order_id)
    old_status = order.status
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            
            # Send email based on status change
            try:
                if old_status == 'pending' and new_status == 'processing':
                    send_order_confirmed_email(order)
                    messages.success(request, f'Order #{order.id} confirmed. Confirmation email sent to customer.')
                elif new_status == 'shipped':
                    send_order_shipped_email(order)
                    messages.success(request, f'Order #{order.id} marked as shipped. Shipping email sent to customer.')
                elif new_status == 'delivered':
                    send_order_delivered_email(order)
                    messages.success(request, f'Order #{order.id} marked as delivered. Delivery confirmation sent to customer.')
                elif new_status == 'cancelled':
                    send_order_cancelled_email(order)
                    messages.success(request, f'Order #{order.id} cancelled. Cancellation email sent to customer.')
                else:
                    messages.success(request, f'Order #{order.id} status updated to {order.get_status_display()}.')
            except Exception as e:
                messages.success(request, f'Order #{order.id} status updated (email sending failed).')
                print(f"Email error: {e}")
            
            return redirect('orders:admin_order_detail', order_id=order.id)
    
    return render(request, 'admin/orders/admin_order_detail.html', {'order': order})