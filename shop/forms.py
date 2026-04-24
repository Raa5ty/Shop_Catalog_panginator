from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Category


class CategoryForm(forms.ModelForm):
    """Форма для создания и редактирования категории"""
    
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название категории'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Описание категории (необязательно)'}),
        }
    
    def clean_name(self):
        """Валидация: название категории не менее 2 символов"""
        name = self.cleaned_data.get('name')
        if not name or len(name.strip()) < 2:
            raise ValidationError('Название категории должно содержать минимум 2 символа')
        return name.strip()


class ProductForm(forms.ModelForm):
    """Форма для создания и редактирования товара"""
    
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название товара'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена в рублях', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Описание товара (необязательно)'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_price(self):
        """Валидация: цена не может быть отрицательной или нулевой"""
        price = self.cleaned_data.get('price')
        if price is None:
            raise ValidationError('Укажите цену товара')
        if price < 0:
            raise ValidationError('Цена не может быть отрицательной')
        if price == 0:
            raise ValidationError('Цена не может быть равна 0')
        return price
    
    def clean_name(self):
        """Валидация: название товара не менее 3 символов"""
        name = self.cleaned_data.get('name')
        if not name or len(name.strip()) < 3:
            raise ValidationError('Название товара должно содержать минимум 3 символа')
        return name.strip()