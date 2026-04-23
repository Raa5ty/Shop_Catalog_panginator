from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from .models import Product, Order, OrderItem


class ModelsTest(TestCase):
    """Тесты моделей"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.product = Product.objects.create(
            name='Тестовый товар',
            category='electronics',
            price=999.99
        )
        self.order = Order.objects.create(user=self.user)
    
    def test_product_creation(self):
        """Тест создания товара"""
        self.assertEqual(self.product.name, 'Тестовый товар')
        self.assertEqual(self.product.category, 'electronics')
        self.assertEqual(float(self.product.price), 999.99)
        self.assertIsNotNone(self.product.date_added)
        self.assertEqual(str(self.product), 'Тестовый товар')
    
    def test_order_creation(self):
        """Тест создания заказа"""
        self.assertEqual(self.order.user.username, 'testuser')
        self.assertIsNotNone(self.order.created_at)
        self.assertIn(str(self.order.id), str(self.order))
    
    def test_order_item_creation(self):
        """Тест добавления товара в заказ"""
        order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=3
        )
        self.assertEqual(order_item.quantity, 3)
        self.assertEqual(order_item.product.name, 'Тестовый товар')
        self.assertEqual(self.order.orderitem_set.count(), 1)


class FilterAndSortTest(TestCase):
    """Тесты фильтрации и сортировки"""
    
    def setUp(self):
        self.client = Client()
        now = timezone.now()
        
        # Создаём тестовые товары
        self.product1 = Product.objects.create(
            name='Смартфон',
            category='electronics',
            price=30000,
            date_added=now - timedelta(days=5)
        )
        self.product2 = Product.objects.create(
            name='Наушники',
            category='electronics',
            price=5000,
            date_added=now - timedelta(days=15)
        )
        self.product3 = Product.objects.create(
            name='Футболка',
            category='clothing',
            price=1500,
            date_added=now - timedelta(days=25)
        )
        
        # Создаём заказы для популярности
        user = User.objects.create_user(username='testuser', password='testpass')
        order = Order.objects.create(user=user)
        OrderItem.objects.create(order=order, product=self.product1, quantity=1)
        OrderItem.objects.create(order=order, product=self.product1, quantity=1)
        OrderItem.objects.create(order=order, product=self.product2, quantity=1)
    
    def test_filter_by_category(self):
        """Фильтрация по категории"""
        response = self.client.get('/shop/ajax/product-catalog/', {'category': 'electronics'})
        data = response.json()
        
        self.assertEqual(len(data['products']), 2)
        for product in data['products']:
            self.assertEqual(product['category'], 'electronics')
    
    def test_filter_by_category_clothing(self):
        """Фильтрация по категории одежда"""
        response = self.client.get('/shop/ajax/product-catalog/', {'category': 'clothing'})
        data = response.json()
        
        self.assertEqual(len(data['products']), 1)
        self.assertEqual(data['products'][0]['name'], 'Футболка')
    
    def test_sort_by_price_asc(self):
        """Сортировка по цене (возрастание)"""
        response = self.client.get('/shop/ajax/product-catalog/', {'sort': 'price_asc'})
        data = response.json()
        
        prices = [p['price'] for p in data['products']]
        self.assertEqual(prices, sorted(prices))
        self.assertEqual(prices[0], 1500)
        self.assertEqual(prices[-1], 30000)
    
    def test_sort_by_price_desc(self):
        """Сортировка по цене (убывание)"""
        response = self.client.get('/shop/ajax/product-catalog/', {'sort': 'price_desc'})
        data = response.json()
        
        prices = [p['price'] for p in data['products']]
        self.assertEqual(prices, sorted(prices, reverse=True))
        self.assertEqual(prices[0], 30000)
        self.assertEqual(prices[-1], 1500)
    
    def test_sort_by_popularity(self):
        """Сортировка по популярности"""
        response = self.client.get('/shop/ajax/product-catalog/', {'sort': 'popularity_desc'})
        data = response.json()
        
        order_counts = [p['order_count'] for p in data['products']]
        self.assertEqual(order_counts, sorted(order_counts, reverse=True))
        self.assertEqual(data['products'][0]['name'], 'Смартфон')
    
    def test_sort_by_date_desc(self):
        """Сортировка по дате (новые сначала)"""
        response = self.client.get('/shop/ajax/product-catalog/', {'sort': 'date_desc'})
        data = response.json()
        
        # Самый новый товар должен быть первым
        self.assertEqual(data['products'][0]['name'], 'Смартфон')


class PaginationTest(TestCase):
    """Тесты пагинации"""
    
    def setUp(self):
        self.client = Client()
        # Создаём 25 товаров
        for i in range(25):
            Product.objects.create(
                name=f'Товар {i+1}',
                category='electronics',
                price=1000 + i * 100
            )
    
    def test_pagination_limit(self):
        """Проверка лимита 10 товаров на страницу"""
        response = self.client.get('/shop/ajax/product-catalog/')
        data = response.json()
        
        self.assertEqual(len(data['products']), 10)
        self.assertEqual(data['pagination']['total_pages'], 3)
        self.assertEqual(data['total_count'], 25)
    
    def test_pagination_second_page(self):
        """Проверка второй страницы"""
        response = self.client.get('/shop/ajax/product-catalog/', {'page': 2})
        data = response.json()
        
        self.assertEqual(len(data['products']), 10)
        self.assertEqual(data['pagination']['current_page'], 2)
    
    def test_pagination_invalid_page(self):
        """Проверка несуществующей страницы"""
        response = self.client.get('/shop/ajax/product-catalog/', {'page': 999})
        data = response.json()
        
        # Должна быть первая страница
        self.assertEqual(data['pagination']['current_page'], 1)


class ViewsTest(TestCase):
    """Тесты страниц"""
    
    def setUp(self):
        self.client = Client()
        Product.objects.create(
            name='Тестовый товар',
            category='electronics',
            price=1000
        )
        User.objects.create_user(username='testuser', password='testpass')
    
    def test_catalog_page(self):
        """Страница каталога"""
        response = self.client.get('/shop/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product_catalog.html')
    
    def test_popular_page(self):
        """Страница популярных товаров"""
        response = self.client.get('/shop/popular/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/popular_products.html')
    
    def test_recent_orders_page(self):
        """Страница недавних заказов"""
        response = self.client.get('/shop/recent-orders/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/recent_orders.html')
    
    def test_ajax_endpoint(self):
        """AJAX endpoint работает"""
        response = self.client.get('/shop/ajax/product-catalog/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
    
    def test_root_redirect(self):
        """Корневой URL редиректит на каталог"""
        response = self.client.get('/')
        self.assertRedirects(response, '/shop/', status_code=302)