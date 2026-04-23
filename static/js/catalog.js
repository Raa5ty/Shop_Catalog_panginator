// catalog.js - AJAX фильтрация и сортировка

class ProductCatalog {
    constructor() {
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadProducts();
    }
    
    bindEvents() {
        // Отслеживаем изменения всех полей фильтрации
        const filterForm = document.getElementById('filter-form');
        const inputs = filterForm.querySelectorAll('select, input');
        
        inputs.forEach(input => {
            input.addEventListener('change', () => {
                this.currentPage = 1;
                this.loadProducts();
            });
        });
    }
    
    getQueryParams() {
        const formData = new FormData(document.getElementById('filter-form'));
        const params = new URLSearchParams();
        
        for (let [key, value] of formData.entries()) {
            if (value && value !== '') {
                params.append(key, value);
            }
        }
        
        // Добавляем текущую страницу
        const page = this.currentPage || 1;
        params.append('page', page);
        
        return params;
    }
    
    loadProducts() {
        const params = this.getQueryParams();
        
        fetch(`/shop/ajax/product-catalog/?${params.toString()}`)
            .then(response => response.json())
            .then(data => {
                this.updateCategories(data.categories);
                this.updateResultsCount(data.total_count);
                this.renderProducts(data.products);
                this.renderPagination(data.pagination);
            })
            .catch(error => {
                console.error('Error:', error);
                this.showError();
            });
    }
    
    loadProductsWithPage(page) {
        this.currentPage = parseInt(page);
        this.loadProducts();
    }
    
    updateCategories(categories) {
        const categorySelect = document.getElementById('category');
        // Сохраняем выбранное значение
        const selectedValue = categorySelect.value;
        
        // Очищаем опции кроме первой
        while (categorySelect.options.length > 1) {
            categorySelect.remove(1);
        }
        
        // Добавляем новые категории
        categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat;
            option.textContent = cat;
            categorySelect.appendChild(option);
        });
        
        // Восстанавливаем выбранное значение
        if (selectedValue) {
            categorySelect.value = selectedValue;
        }
    }
    
    updateResultsCount(count) {
        const countElement = document.getElementById('total-count');
        if (countElement) {
            const text = this.getDeclension(count, ['товар', 'товара', 'товаров']);
            countElement.textContent = `Найдено: ${count} ${text}`;
        }
    }
    
    getDeclension(number, titles) {
        const cases = [2, 0, 1, 1, 1, 2];
        return titles[(number % 100 > 4 && number % 100 < 20) ? 2 : cases[(number % 10 < 5) ? number % 10 : 5]];
    }
    
    renderProducts(products) {
        const productList = document.getElementById('product-list');
        
        if (!products || products.length === 0) {
            productList.innerHTML = '<div class="loading">😔 Товары не найдены</div>';
            return;
        }
        
        productList.innerHTML = products.map(product => `
            <div class="product-card">
                <div class="product-content">
                    <div class="product-name">${this.escapeHtml(product.name)}</div>
                    <div class="product-category">${this.escapeHtml(product.category)}</div>
                    <div class="product-price">${this.formatPrice(product.price)} ₽</div>
                    <div class="product-stats">
                        <div>📅 Добавлен: ${product.date_added}</div>
                        <div>🛒 Заказов: ${product.order_count}</div>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    renderPagination(pagination) {
        const paginationContainer = document.getElementById('pagination');
        
        if (!pagination || pagination.total_pages <= 1) {
            paginationContainer.innerHTML = '';
            return;
        }
        
        let html = '';
        
        // Кнопка "Первая"
        if (pagination.has_previous) {
            html += `<a href="#" data-page="1">«« Первая</a>`;
            html += `<a href="#" data-page="${pagination.previous_page_number}">« Предыдущая</a>`;
        }
        
        // Текущая страница
        html += `<span class="current-page">${pagination.current_page}</span>`;
        
        // Кнопка "Следующая"
        if (pagination.has_next) {
            html += `<a href="#" data-page="${pagination.next_page_number}">Следующая »</a>`;
            html += `<a href="#" data-page="${pagination.total_pages}">Последняя »»</a>`;
        }
        
        paginationContainer.innerHTML = html;
        
        // Привязываем обработчики
        paginationContainer.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.dataset.page;
                if (page) {
                    this.loadProductsWithPage(page);
                }
            });
        });
    }
    
    formatPrice(price) {
        return new Intl.NumberFormat('ru-RU').format(price);
    }
    
    escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
    
    showError() {
        const productList = document.getElementById('product-list');
        productList.innerHTML = '<div class="loading">❌ Ошибка загрузки данных. Попробуйте позже.</div>';
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.catalog = new ProductCatalog();
});