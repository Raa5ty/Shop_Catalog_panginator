from django.urls import path
from . import views

urlpatterns = [
    # Главная страница каталога (с AJAX)
    path('', views.product_catalog_page, name='product_catalog'),
    
    # AJAX endpoint для каталога
    path('ajax/product-catalog/', views.product_catalog_ajax, name='product_catalog_ajax'),
    
    # Дополнительные страницы
    path('popular/', views.popular_products_page, name='popular_products'),
    path('recent-orders/', views.recent_orders_page, name='recent_orders'),
    
]