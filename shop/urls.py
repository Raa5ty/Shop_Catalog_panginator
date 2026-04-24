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
    path('analytics/', views.analytics, name='analytics'),
    
    # Категории
    path('categories/', views.category_list, name='category_list'),
    path('category/create/', views.category_create, name='category_create'),
    path('category/<int:pk>/edit/', views.category_update, name='category_update'),
    path('category/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Продукты
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/create/', views.product_create, name='product_create'),
    path('product/<int:pk>/edit/', views.product_update, name='product_update'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),
]