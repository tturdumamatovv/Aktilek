from django import forms
from apps.product.models import ProductSize, Product, Category, SimilarProduct
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


class SimilarProductInlineForm(forms.ModelForm):
    class Meta:
        model = SimilarProduct
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get("product")
        similar_product = cleaned_data.get("similar_product")

        # Проверяем, что продукт не совпадает с похожим продуктом
        if product == similar_product:
            raise ValidationError("Нельзя выбрать тот же продукт в качестве похожего.")

        # Проверяем на дубликаты
        if SimilarProduct.objects.filter(product=product, similar_product=similar_product).exists():
            raise ValidationError("Этот продукт уже добавлен как похожий.")

        return cleaned_data
