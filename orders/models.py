from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from decimal import Decimal


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    SHIPPING_METHOD_CHOICES = [
        ('standard', 'Standard Shipping (5-7 days) - FREE over £50'),
        ('express', 'Express Shipping (2-3 days) - £9.99'),
        ('next_day', 'Next Day Delivery - £14.99'),
        ('international', 'International Shipping (10-15 days) - £24.99'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('full', 'Pay Full Amount Online'),
        ('partial', 'Pay 50% Now, 50% on Delivery'),
    ]
    
    # User and Order Info
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Shipping Information
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address_line_1 = models.CharField(max_length=250)
    address_line_2 = models.CharField(max_length=250, blank=True)
    city = models.CharField(max_length=100)
    county = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=20)
    
    # Shipping Method
    shipping_method = models.CharField(
        max_length=20, 
        choices=SHIPPING_METHOD_CHOICES, 
        default='standard'
    )
    estimated_delivery = models.CharField(max_length=100, blank=True)
    
    # Payment Method
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
        default='full'
    )
    
    # Order Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid = models.BooleanField(default=False)
    partial_payment_received = models.BooleanField(default=False)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    vat = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Partial Payment Amounts
    amount_paid_online = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Payment
    stripe_payment_intent = models.CharField(max_length=250, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f'Order {self.id}'
    
    def get_total_cost(self):
        return self.total_amount
    
    def get_payment_status_display_custom(self):
        """Custom payment status display"""
        if self.payment_method == 'full':
            return 'Paid' if self.paid else 'Payment Pending'
        else:  # partial
            if self.paid:
                return 'Fully Paid'
            elif self.partial_payment_received:
                return f'50% Paid (£{self.remaining_amount} due on delivery)'
            else:
                return '50% Payment Pending'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    size = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f'{self.quantity} x {self.product.name} ({self.size})'
    
    def get_total_price(self):
        return self.price * self.quantity