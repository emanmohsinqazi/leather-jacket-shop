from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0
    readonly_fields = ['get_total_price']
    
    def get_total_price(self, obj):
        return f'£{obj.get_total_price()}'
    get_total_price.short_description = 'Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'full_name',
        'email',
        'status',
        'total_amount',
        'paid',
        'shipping_method',
        'created_at'
    ]
    list_filter = ['status', 'paid', 'created_at', 'shipping_method']
    search_fields = ['id', 'full_name', 'email', 'phone', 'postcode']
    readonly_fields = [
        'created_at',
        'updated_at',
        'subtotal',
        'shipping_cost',
        'vat',
        'total_amount',
        'stripe_payment_intent'
    ]
    
    fieldsets = (
        ('Order Information', {
            'fields': (
                'user',
                'status',
                'paid',
                'created_at',
                'updated_at'
            )
        }),
        ('Shipping Information', {
            'fields': (
                'full_name',
                'email',
                'phone',
                'address_line_1',
                'address_line_2',
                'city',
                'county',
                'postcode',
                'shipping_method',
                'estimated_delivery'
            )
        }),
        ('Pricing', {
            'fields': (
                'subtotal',
                'shipping_cost',
                'vat',
                'total_amount'
            )
        }),
        ('Payment', {
            'fields': (
                'stripe_payment_intent',
            )
        }),
    )
    
    inlines = [OrderItemInline]
    
    def get_readonly_fields(self, request, obj=None):
        # If editing an existing order, make most fields read-only
        if obj:
            return self.readonly_fields + [
                'user',
                'full_name',
                'email',
                'phone',
                'address_line_1',
                'address_line_2',
                'city',
                'county',
                'postcode',
                'shipping_method'
            ]
        return self.readonly_fields


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'size', 'quantity', 'price', 'get_total']
    list_filter = ['order__status', 'order__created_at']
    search_fields = ['order__id', 'product__name']
    raw_id_fields = ['order', 'product']
    
    def get_total(self, obj):
        return f'£{obj.get_total_price()}'
    get_total.short_description = 'Total Price'