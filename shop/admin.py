from django.contrib import admin
from .models import Product, Order, OrderItem, Category


class OrderItemInline(admin.TabularInline):
    """Inline-форма для добавления товаров прямо в заказе"""
    model = OrderItem
    extra = 1
    raw_id_fields = ('product',)
    fields = ('product', 'quantity')
    show_change_link = True

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'products_count')
    list_display_links = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description')
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def products_count(self, obj):
        """Количество товаров в категории"""
        return obj.products.count()  
    products_count.short_description = 'Товаров'
    products_count.admin_order_field = 'products__count'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'date_added', 'get_order_count', 'image_preview')
    list_display_links = ('name',)
    list_filter = ('category', 'date_added')
    search_fields = ('name', 'category')
    ordering = ('-date_added',)
    readonly_fields = ('date_added',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'category', 'price', 'description')
        }),
        ('Изображение', {
            'fields': ('image',),
            'classes': ('wide',)
        }),
        ('Системная информация', {
            'fields': ('date_added',),
            'classes': ('collapse',)
        }),
    )
    
    def get_order_count(self, obj):
        """Количество заказов товара"""
        return obj.orderitem_set.count()
    get_order_count.short_description = 'Заказов'
    
    def image_preview(self, obj):
        """Превью изображения в админке"""
        if obj.image:
            from django.utils.html import format_html
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image.url)
        return "Нет фото"
    image_preview.short_description = 'Фото'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'get_total_items', 'get_total_value')
    list_display_links = ('id', 'user')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'user__email', 'id')
    readonly_fields = ('created_at',)
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Информация о заказе', {
            'fields': ('user', 'created_at')
        }),
    )
    
    def get_total_items(self, obj):
        """Общее количество товаров в заказе"""
        return sum(item.quantity for item in obj.orderitem_set.all())
    get_total_items.short_description = 'Кол-во товаров'
    
    def get_total_value(self, obj):
        """Общая стоимость заказа"""
        total = sum(item.product.price * item.quantity for item in obj.orderitem_set.all())
        return f'{total:,.0f} ₽'
    get_total_value.short_description = 'Сумма заказа'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'get_item_total')
    list_display_links = ('id',)
    list_filter = ('order__user', 'product__category')
    search_fields = ('order__id', 'product__name')
    autocomplete_fields = ('order', 'product')
    readonly_fields = ('get_item_total',)
    
    fieldsets = (
        ('Связи', {
            'fields': ('order', 'product')
        }),
        ('Количество', {
            'fields': ('quantity',)
        }),
        ('Информация', {
            'fields': ('get_item_total',),
            'classes': ('collapse',)
        }),
    )
    
    def get_item_total(self, obj):
        """Стоимость позиции заказа"""
        total = obj.product.price * obj.quantity
        return f'{total:,.0f} ₽'
    get_item_total.short_description = 'Сумма'