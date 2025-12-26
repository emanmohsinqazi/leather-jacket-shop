from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def send_order_created_email(order):
    """
    Send email to customer when order is created (pending status)
    """
    subject = f'Order #{order.id} Received - UK Leather Jackets'
    
    # Email content
    message = f"""
Dear {order.full_name},

Thank you for your order! We have received your order and it is currently being processed.

ORDER DETAILS:
--------------
Order Number: #{order.id}
Order Date: {order.created_at.strftime('%B %d, %Y at %H:%M')}
Status: Pending

ITEMS ORDERED:
"""
    
    # Add items
    for item in order.items.all():
        message += f"\n- {item.product.name} (Size: {item.size}) x {item.quantity} - £{item.get_total_price()}"
    
    # Add pricing
    message += f"""

ORDER SUMMARY:
--------------
Subtotal: £{order.subtotal}
Shipping: £{order.shipping_cost} ({order.get_shipping_method_display()})
VAT (20%): £{order.vat}
Total: £{order.total_amount}

SHIPPING ADDRESS:
-----------------
{order.full_name}
{order.address_line_1}
{order.address_line_2 if order.address_line_2 else ''}
{order.city}, {order.county if order.county else ''}
{order.postcode}
United Kingdom

We will send you another email once your order has been confirmed and shipped.

You can track your order status at any time by logging into your account.

If you have any questions, please contact us:
Email: info@ukleatherjackets.co.uk
Phone: +44 20 1234 5678

Thank you for shopping with UK Leather Jackets!

Best regards,
UK Leather Jackets Team
"""
    
    # Send email
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending order created email: {e}")
        return False


def send_order_confirmed_email(order):
    """
    Send email to customer when admin changes status from pending to processing
    """
    subject = f'Order #{order.id} Confirmed - UK Leather Jackets'
    
    message = f"""
Dear {order.full_name},

Great news! Your order has been confirmed and is now being prepared for shipment.

ORDER DETAILS:
--------------
Order Number: #{order.id}
Status: Processing
Estimated Delivery: {order.estimated_delivery}

ITEMS IN YOUR ORDER:
"""
    
    # Add items
    for item in order.items.all():
        message += f"\n- {item.product.name} (Size: {item.size}) x {item.quantity} - £{item.get_total_price()}"
    
    message += f"""

Total: £{order.total_amount}

DELIVERY INFORMATION:
---------------------
Shipping Method: {order.get_shipping_method_display()}
Estimated Delivery: {order.estimated_delivery}

Delivery Address:
{order.full_name}
{order.address_line_1}
{order.address_line_2 if order.address_line_2 else ''}
{order.city}, {order.county if order.county else ''}
{order.postcode}

We will send you a shipping confirmation email with tracking information once your order has been dispatched.

Thank you for your patience!

Best regards,
UK Leather Jackets Team

---
Need help? Contact us:
Email: info@ukleatherjackets.co.uk
Phone: +44 20 1234 5678
"""
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending order confirmed email: {e}")
        return False


def send_order_shipped_email(order):
    """
    Send email to customer when order is shipped
    """
    subject = f'Order #{order.id} Shipped - UK Leather Jackets'
    
    message = f"""
Dear {order.full_name},

Your order has been shipped! 📦

ORDER DETAILS:
--------------
Order Number: #{order.id}
Status: Shipped
Estimated Delivery: {order.estimated_delivery}

Your order is on its way and should arrive within {order.estimated_delivery}.

TRACKING INFORMATION:
---------------------
Shipping Method: {order.get_shipping_method_display()}

Delivery Address:
{order.full_name}
{order.address_line_1}
{order.address_line_2 if order.address_line_2 else ''}
{order.city}, {order.county if order.county else ''}
{order.postcode}
United Kingdom

ITEMS SHIPPED:
"""
    
    for item in order.items.all():
        message += f"\n- {item.product.name} (Size: {item.size}) x {item.quantity}"
    
    message += f"""

Please ensure someone is available to receive your delivery.

If you have any questions about your shipment, please contact us.

Thank you for shopping with UK Leather Jackets!

Best regards,
UK Leather Jackets Team

---
Need help? Contact us:
Email: info@ukleatherjackets.co.uk
Phone: +44 20 1234 5678
"""
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending order shipped email: {e}")
        return False


def send_order_delivered_email(order):
    """
    Send email to customer when order is delivered
    """
    subject = f'Order #{order.id} Delivered - UK Leather Jackets'
    
    message = f"""
Dear {order.full_name},

Your order has been delivered! 🎉

We hope you love your new leather jacket(s)!

ORDER DETAILS:
--------------
Order Number: #{order.id}
Status: Delivered
Delivery Date: {order.updated_at.strftime('%B %d, %Y')}

ITEMS DELIVERED:
"""
    
    for item in order.items.all():
        message += f"\n- {item.product.name} (Size: {item.size}) x {item.quantity}"
    
    message += f"""

CARE INSTRUCTIONS:
------------------
To keep your leather jacket looking great:
- Avoid prolonged exposure to water
- Store in a cool, dry place
- Use leather conditioner periodically
- Professional cleaning recommended

HOW WAS YOUR EXPERIENCE?
-------------------------
We'd love to hear your feedback! Please consider leaving a review on our website.

If you have any issues with your order, please contact us within 30 days for our hassle-free returns policy.

Thank you for choosing UK Leather Jackets!

Best regards,
UK Leather Jackets Team

---
Need help? Contact us:
Email: info@ukleatherjackets.co.uk
Phone: +44 20 1234 5678
"""
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending order delivered email: {e}")
        return False


def send_order_cancelled_email(order):
    """
    Send email to customer when order is cancelled
    """
    subject = f'Order #{order.id} Cancelled - UK Leather Jackets'
    
    message = f"""
Dear {order.full_name},

Your order has been cancelled.

ORDER DETAILS:
--------------
Order Number: #{order.id}
Status: Cancelled
Total Amount: £{order.total_amount}

If you did not request this cancellation or if you have any questions, please contact us immediately.

REFUND INFORMATION:
-------------------
If payment was processed, a full refund will be issued to your original payment method within 5-10 business days.

We apologize for any inconvenience this may have caused.

If you'd like to place a new order, please visit our website:
www.ukleatherjackets.co.uk

Thank you for your understanding.

Best regards,
UK Leather Jackets Team

---
Need help? Contact us:
Email: info@ukleatherjackets.co.uk
Phone: +44 20 1234 5678
"""
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending order cancelled email: {e}")
        return False