from django import forms

from apps.pages.models import MethodsOfPayment
from apps.product.models import ProductSize, Product, Category, Characteristic, Color, Tag
from django.utils.translation import gettext_lazy as _


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


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем фильтрацию категорий, чтобы отображать все доступные категории
        self.fields['category'].queryset = Category.objects.all()

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
