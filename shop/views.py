from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from datetime import timedelta
from django.contrib import messages
from shop.forms import CategoryForm, ProductForm
from .models import Category, User, Order, Product, OrderItem
from django.db.models import Sum, Avg, Min, Max


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
        products = products.filter(category__name=category)
    
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
            'category': product.category.name if product.category else '',
            'price': float(product.price),
            'date_added': product.date_added.strftime('%d.%m.%Y'),
            'order_count': product.order_count,
            'image': product.image.url if product.image and hasattr(product.image, 'url') else '/static/images/no-image.png',
        })
    
    categories = list(Category.objects.values_list('name', flat=True))
    
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

# ===== СТРАНИЦА СПИСКА КАТЕГОРИЙ =====
def category_list(request):
    categories = Category.objects.annotate(
        products_count=Count('products')
    )
    return render(request, 'shop/category_list.html', {'categories': categories})

# ===== СТРАНИЦА СОЗДАНИЯ КАТЕГОРИИ =====
def category_create(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        category = form.save()
        messages.success(request, f'Категория "{category.name}" успешно создана!')
        return redirect('category_list')
    return render(request, 'shop/category_form.html', {'form': form, 'title': 'Создание категории'})

# ===== СТРАНИЦА РЕДАКТИРОВАНИЯ КАТЕГОРИИ =====
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        messages.success(request, f'Категория "{category.name}" успешно обновлена!')
        return redirect('category_list')
    return render(request, 'shop/category_form.html', {'form': form, 'title': 'Редактирование категории'})

# ===== СТРАНИЦА УДАЛЕНИЯ КАТЕГОРИИ =====
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    products_count = category.products.count()
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Категория "{category_name}" успешно удалена!')
        return redirect('category_list')
    
    return render(request, 'shop/category_confirm_delete.html', {
        'category': category,
        'products_count': products_count
    })

# ===== СТРАНИЦА ДЕТАЛЬНОГО ПРОСМОТРА ТОВАРА =====
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})

# ==== СТРАНИЦА СОЗДАНИЯ ТОВАРА =====
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        product = form.save()
        messages.success(request, f'Товар "{product.name}" успешно создан!')
        return redirect('product_detail', pk=product.pk)
    return render(request, 'shop/product_form.html', {'form': form, 'title': 'Создание товара'})

# ==== СТРАНИЦА РЕДАКТИРОВАНИЯ ТОВАРА =====
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, f'Товар "{product.name}" успешно обновлён!')
        return redirect('product_detail', pk=product.pk)
    return render(request, 'shop/product_form.html', {'form': form, 'title': 'Редактирование товара'})

# ==== СТРАНИЦА УДАЛЕНИЯ ТОВАРА =====
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Товар "{product_name}" успешно удалён!')
        return redirect('product_catalog')
    return render(request, 'shop/product_confirm_delete.html', {'product': product})

# ==== СТРАНИЦА АНАЛИТИКИ =====
def analytics(request):
    # Общая статистика по всем товарам
    total_products = Product.objects.count()
    total_value = Product.objects.aggregate(total=Sum('price'))['total'] or 0
    avg_price = Product.objects.aggregate(avg=Avg('price'))['avg'] or 0
    min_price = Product.objects.aggregate(min=Min('price'))['min'] or 0
    max_price = Product.objects.aggregate(max=Max('price'))['max'] or 0
    
    # Статистика по категориям
    category_stats = Category.objects.annotate(
        products_count=Count('products'),
        total_value=Sum('products__price'),
        avg_price=Avg('products__price'),
        min_price=Min('products__price'),
        max_price=Max('products__price')
    ).filter(products_count__gt=0).order_by('-total_value')
    
    context = {
        'total_products': total_products,
        'total_value': total_value,
        'avg_price': avg_price,
        'min_price': min_price,
        'max_price': max_price,
        'category_stats': category_stats,
    }
    
    return render(request, 'shop/analytics.html', context)