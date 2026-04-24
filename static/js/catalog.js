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
            productList.innerHTML = '<div class="col-12"><div class="alert alert-info text-center">😔 Товары не найдены</div></div>';
            return;
        }
        
        productList.innerHTML = products.map(product => `
            <div class="col-md-6 col-lg-4 col-xl-3 mb-4">
                <div class="card h-100">
                    <div class="text-center pt-2">
                        <a href="/shop/product/${product.id}/">
                            <img src="${product.image}" style="height: 100px; width: auto; object-fit: contain;" alt="${this.escapeHtml(product.name)}">
                        </a>
                    </div>
                    <div class="card-body">
                        <h5 class="card-title">
                            <a href="/shop/product/${product.id}/" class="text-dark text-decoration-none">${this.escapeHtml(product.name)}</a>
                        </h5>
                        <p class="card-text text-muted small">${this.escapeHtml(product.category)}</p>
                        <h4 class="text-primary">${this.formatPrice(product.price)} ₽</h4>
                    </div>
                    <div class="card-footer bg-white text-muted small">
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
        
        let html = '<ul class="pagination">';
        
        if (pagination.has_previous) {
            html += `<li class="page-item"><a class="page-link" href="#" data-page="1">««</a></li>`;
            html += `<li class="page-item"><a class="page-link" href="#" data-page="${pagination.previous_page_number}">«</a></li>`;
        }
        
        html += `<li class="page-item active"><span class="page-link">${pagination.current_page}</span></li>`;
        
        if (pagination.has_next) {
            html += `<li class="page-item"><a class="page-link" href="#" data-page="${pagination.next_page_number}">»</a></li>`;
            html += `<li class="page-item"><a class="page-link" href="#" data-page="${pagination.total_pages}">»»</a></li>`;
        }
        
        html += '</ul>';
        paginationContainer.innerHTML = html;
        
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