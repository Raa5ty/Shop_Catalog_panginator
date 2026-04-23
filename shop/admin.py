
# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ("name", "category", "price")
#     list_filter = ("category", "price")
#     search_fields = ("name", "category")

# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ("user", "created_at")
#     list_filter = ("user", "created_at")
#     search_fields = ("user", "created_at")

# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ("order", "product", "quantity")
#     list_filter = ("order", "product")
#     search_fields = ("order", "product")

from django.contrib import admin
from .models import Product, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Inline-форма для добавления товаров прямо в заказе"""
    model = OrderItem
    extra = 1
    raw_id_fields = ('product',)
    fields = ('product', 'quantity')
    show_change_link = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'date_added', 'get_order_count')
    list_display_links = ('name',)
    list_filter = ('category', 'date_added')
    search_fields = ('name', 'category')
    ordering = ('-date_added',)
    readonly_fields = ('date_added',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'category', 'price')
        }),
        ('Системная информация', {
            'fields': ('date_added',),
            'classes': ('collapse',)
        }),
    )
    
    def get_order_count(self, obj):
        """Количество заказов товара"""
        return obj.orderitem_set.count()
    get_order_count.short_description = 'Количество заказов'
    get_order_count.admin_order_field = 'order_count'


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