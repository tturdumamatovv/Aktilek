from django import forms
from apps.product.models import ProductSize, Product, Category


class ProductSizeForm(forms.ModelForm):
    class Meta:
        model = ProductSize
        fields = ['product', 'sizes', 'color']

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
