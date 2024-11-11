from django import forms

from apps.pages.models import MethodsOfPayment
from apps.product.models import ProductSize, Product, Category, Characteristic, Color, Tag, ProductImage

from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.core.exceptions import ValidationError


class ProductSizeForm(forms.ModelForm):
    class Meta:
        model = ProductSize
        fields = ['product', 'size', 'color', 'quantity', 'price', 'discounted_price', 'bonus_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'product' in self.initial:
            product = self.initial['product']
        elif 'product' in self.data:
            product = self.data['product']
        else:
            product = None

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')

        # Check if the product has associated images
        if product and not ProductImage.objects.filter(product=product).exists():
            raise forms.ValidationError("Each product size must have at least one associated image.")

        return cleaned_data


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем фильтрацию категорий, чтобы отображать все доступные категории
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].label_from_instance = lambda obj: format_html(
            '&nbsp;' * (obj.level * 4) + str(obj)
        )

        if self.instance and self.instance.pk:
            # Исключаем текущий продукт из списка выбора похожих продуктов
            self.fields['similar_products'].queryset = Product.objects.exclude(pk=self.instance.pk)



    def clean(self):
        cleaned_data = super().clean()
        # Проверяем обязательные поля для каждого языка
        languages = ['ru', 'en', 'ky']  # Add your language codes here

        for lang in languages:
            name_field = f'name_{lang}'
            description_field = f'description_{lang}'

            if not cleaned_data.get(name_field):
                self.add_error(name_field, _("This field is required."))

            if not cleaned_data.get(description_field):
                self.add_error(description_field, _("This field is required."))

        return cleaned_data

class CharacteristicInlineForm(forms.ModelForm):
    class Meta:
        model = Characteristic
        fields = '__all__'  # Include all fields, or specify which ones you want

    def clean(self):
        cleaned_data = super().clean()
        languages = ['ru', 'en', 'ky']  # Add your language codes here

        for lang in languages:
            name_field = f'name_{lang}'
            value_field = f'value_{lang}'

            if not cleaned_data.get(name_field):
                self.add_error(name_field, _("This field is required."))

            if not cleaned_data.get(value_field):
                self.add_error(value_field, _("This field is required."))

        return cleaned_data


class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'  # Включить все поля или указать, какие именно нужны

    def clean(self):
        cleaned_data = super().clean()
        languages = ['ru', 'en', 'ky']  # Добавьте ваши коды языков здесь

        for lang in languages:
            name_field = f'name_{lang}'

            if not cleaned_data.get(name_field):
                self.add_error(name_field, _("This field is required."))

        return cleaned_data

class ColorAdminForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = '__all__'  # Include all fields or specify which ones you want

    def clean(self):
        cleaned_data = super().clean()
        languages = ['ru', 'en', 'ky']  # Add your language codes here

        for lang in languages:
            name_field = f'name_{lang}'  # Assuming the translated field names are like name_ru, name_en, etc.

            if not cleaned_data.get(name_field):
                self.add_error(name_field, _("This field is required."))

        return cleaned_data


class TagAdminForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'  # Include all fields or specify which ones you want

    def clean(self):
        cleaned_data = super().clean()
        languages = ['ru', 'en', 'ky']  # Add your language codes here

        for lang in languages:
            name_field = f'name_{lang}'  # Assuming the translated field names are like name_ru, name_en, etc.

            if not cleaned_data.get(name_field):
                self.add_error(name_field, _("This field is required."))

        return cleaned_data


class MethodsOfPaymentAdminForm(forms.ModelForm):
    class Meta:
        model = MethodsOfPayment
        fields = '__all__'  # Include all fields or specify which ones you want

    def clean(self):
        cleaned_data = super().clean()
        languages = ['ru', 'en', 'ky']  # Add your language codes here

        for lang in languages:
            title_field = f'title_{lang}'  # Assuming the translated field names are like title_ru, title_en, etc.
            description_field = f'description_{lang}'

            if not cleaned_data.get(title_field):
                self.add_error(title_field, _("This field is required."))

            if not cleaned_data.get(description_field):
                self.add_error(description_field, _("This field is required."))

        return cleaned_data


class ProductImageInlineForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ('product', 'image', 'color')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter the color field choices based on the related product if it exists
        if self.instance and self.instance.product:
            self.fields['color'].queryset = Color.objects.filter(
                product_colors__product=self.instance.product
            ).distinct()

    def clean_color(self):
        color = self.cleaned_data.get('color')
        product = self.instance.product

        if product:
            # Fetch available colors for the product's variants dynamically
            available_colors = Color.objects.filter(
                product_colors__product=product
            ).distinct()

            # Check if the selected color is within the available colors
            if color and color not in available_colors:
                raise ValidationError(
                    _("Цвет варианта и картинки должны быть одинаковыми.")
                )

        return color
