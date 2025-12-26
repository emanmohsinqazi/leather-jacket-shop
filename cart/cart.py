from decimal import Decimal
from django.conf import settings
from products.models import Product


class Cart:
    """Session-based shopping cart"""
    
    def __init__(self, request):
        """Initialize the cart"""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
    
    def add(self, product, size, quantity=1, override_quantity=False):
        """Add a product to the cart or update its quantity"""
        product_id = str(product.id)
        cart_key = f"{product_id}_{size}"
        
        if cart_key not in self.cart:
            self.cart[cart_key] = {
                'product_id': product_id,
                'size': size,
                'quantity': 0,
                'price': str(product.get_price())
            }
        
        if override_quantity:
            self.cart[cart_key]['quantity'] = quantity
        else:
            self.cart[cart_key]['quantity'] += quantity
        
        self.save()
    
    def save(self):
        """Mark the session as modified"""
        self.session.modified = True
    
    def remove(self, product_id, size):
        """Remove a product from the cart"""
        cart_key = f"{product_id}_{size}"
        if cart_key in self.cart:
            del self.cart[cart_key]
            self.save()
    
    def __iter__(self):
        """Iterate over the items in the cart and get the products from the database"""
        product_ids = [item['product_id'] for item in self.cart.values()]
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        
        for product in products:
            for key, item in cart.items():
                if item['product_id'] == str(product.id):
                    item['product'] = product
                    item['total_price'] = Decimal(item['price']) * item['quantity']
                    item['cart_key'] = key
                    yield item
    
    def __len__(self):
        """Count all items in the cart"""
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_total_price(self):
        """Calculate total price of items in cart"""
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
    
    def clear(self):
        """Remove cart from session"""
        del self.session[settings.CART_SESSION_ID]
        self.save()
    
    def get_items(self):
        """Get all items with product details"""
        items = []
        for item in self:
            items.append(item)
        return items