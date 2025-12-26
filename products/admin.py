from django.contrib import admin
from .models import Category, Product, ProductReview

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'price', 'discount_price',
        'stock_quantity', 'available', 'featured', 'created_at'
    ]
    list_filter = ['available', 'featured', 'gender', 'category', 'created_at']
    list_editable = ['price', 'discount_price', 'stock_quantity', 'available', 'featured']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description', 'color']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price')
        }),
        ('Product Details', {
            'fields': ('gender', 'material', 'color', 'available_sizes')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'available', 'featured')
        }),
        ('Images', {
            'fields': ('main_image', 'image_2', 'image_3')
        }),
    )

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['product__name', 'user__username', 'comment']
    date_hierarchy = 'created_at'