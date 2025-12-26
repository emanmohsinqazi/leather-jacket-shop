from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from .models import Product, Category, ProductReview


def home(request):
    """Home page with featured products"""
    featured_products = Product.objects.filter(featured=True, available=True)[:8]
    categories = Category.objects.all()
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'home.html', context)


def product_list(request):
    """Display all products with filtering and search"""
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Filter by gender
    gender = request.GET.get('gender')
    if gender:
        products = products.filter(gender=gender)
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(color__icontains=query) |
            Q(material__icontains=query)
        )
    
    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:  # newest
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_slug,
        'current_gender': gender,
        'query': query,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    """Display single product details"""
    product = get_object_or_404(Product, slug=slug, available=True)
    
    # Get product reviews
    reviews = product.reviews.all()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    # Get available sizes as list
    available_sizes = [size.strip() for size in product.available_sizes.split(',')]
    
    # Related products (same category)
    related_products = Product.objects.filter(
        category=product.category,
        available=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating,
        'available_sizes': available_sizes,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)


def add_review(request, product_id):
    """Add a review for a product"""
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to add a review.')
        return redirect('users:login')
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        # Check if user already reviewed this product
        if ProductReview.objects.filter(product=product, user=request.user).exists():
            messages.warning(request, 'You have already reviewed this product.')
        else:
            ProductReview.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                comment=comment
            )
            messages.success(request, 'Your review has been added!')
    
    return redirect('products:product_detail', slug=product.slug)