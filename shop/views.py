from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from datetime import timedelta
from .models import User, Order, Product, OrderItem

# ===== НОВЫЙ AJAX VIEW ДЛЯ КАТАЛОГА =====
def product_catalog_ajax(request):
    """
    AJAX view для фильтрации, сортировки и пагинации товаров
    """
    # Базовый запрос с аннотацией количества заказов
    products = Product.objects.annotate(
        order_count=Count('orderitem')
    )
    
    # 1. ФИЛЬТРАЦИЯ
    category = request.GET.get('category')
    if category and category != '':
        products = products.filter(category=category)
    
    min_price = request.GET.get('min_price')
    if min_price and min_price != '':
        products = products.filter(price__gte=float(min_price))
    
    max_price = request.GET.get('max_price')
    if max_price and max_price != '':
        products = products.filter(price__lte=float(max_price))
    
    days_ago = request.GET.get('days_ago')
    if days_ago and days_ago != '':
        try:
            days = int(days_ago)
            cutoff_date = timezone.now() - timedelta(days=days)
            products = products.filter(date_added__gte=cutoff_date)
        except ValueError:
            pass
    
    # 2. СОРТИРОВКА
    sort_by = request.GET.get('sort', 'popularity_desc')
    
    sort_mapping = {
        'popularity_desc': '-order_count',
        'price_asc': 'price',
        'price_desc': '-price',
        'date_asc': 'date_added',
        'date_desc': '-date_added',
    }
    
    sort_field = sort_mapping.get(sort_by, '-order_count')
    products = products.order_by(sort_field)
    
    # 3. ПАГИНАЦИЯ
    page_number = request.GET.get('page', 1)
    paginator = Paginator(products, 10)
    
    try:
        page_obj = paginator.page(page_number)
    except:
        page_obj = paginator.page(1)
    
    # 4. ФОРМИРОВАНИЕ JSON
    products_data = []
    for product in page_obj:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'category': product.category,
            'price': float(product.price),
            'date_added': product.date_added.strftime('%d.%m.%Y'),
            'order_count': product.order_count,
        })
    
    categories = Product.objects.values_list('category', flat=True).distinct()
    
    return JsonResponse({
        'products': products_data,
        'pagination': {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        },
        'total_count': paginator.count,
        'categories': list(categories),
    })


# ===== СТРАНИЦА КАТАЛОГА =====
def product_catalog_page(request):
    """Страница каталога с AJAX фильтрацией"""
    return render(request, 'shop/product_catalog.html')


# ===== СТРАНИЦА НЕДАВНИХ ЗАКАЗОВ (ОБНОВЛЕННАЯ) =====
def recent_orders_page(request):
    """Страница с заказами за последние 30 дней"""
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    
    users_with_recent_orders = User.objects.annotate(
        recent_order_count=Count('order', filter=Q(order__created_at__gte=thirty_days_ago))
    ).filter(recent_order_count__gt=0).order_by('-recent_order_count')
    
    return render(request, 'shop/recent_orders.html', {'users': users_with_recent_orders})


# ===== СТРАНИЦА ПОПУЛЯРНЫХ ТОВАРОВ (ОБНОВЛЕННАЯ) =====
def popular_products_page(request):
    """Страница с популярными товарами"""
    products = Product.objects.annotate(
        order_count=Count('orderitem')
    ).filter(order_count__gt=0).order_by('-order_count')[:20]  # Топ-20
    
    return render(request, 'shop/popular_products.html', {'products': products})