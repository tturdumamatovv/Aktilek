from django import forms
from apps.product.models import ProductSize, Product, Category
from django.core.exceptions import ValidationError


class ProductSizeForm(forms.ModelForm):
    class Meta:
        model = ProductSize
        fields = ['product', 'size', 'color', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'product' in self.initial:
            product = self.initial['product']
        elif 'product' in self.data:
            product = self.data['product']
        else:
            product = None


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтруем категории, чтобы показывать только конечные (у которых нет подкатегорий)
        self.fields['category'].queryset = Category.objects.filter(subcategories__isnull=True)
        if self.instance and self.instance.pk:
            # Исключаем текущий продукт из списка выбора похожих продуктов
            self.fields['similar_products'].queryset = Product.objects.exclude(pk=self.instance.pk)
