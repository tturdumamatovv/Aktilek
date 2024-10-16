from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from unfold.admin import TabularInline, ModelAdmin

from mptt.admin import DraggableMPTTAdmin
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin
from nested_admin import NestedTabularInline, NestedModelAdmin

from .models import (
    Size,
    Category,
    Product,
    ProductSize,
    Topping,
    Tag,
    Characteristic,
    Review,
    Color,
    ProductImage,
    Country,
    Gender
)
from .forms import ProductSizeForm, ProductAdminForm


class ExcludeBaseFieldsMixin(ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        base_fields = getattr(self, 'exclude_base_fields', [])
        for field_name in base_fields:
            if field_name in form.base_fields:
                del form.base_fields[field_name]
        return form


@admin.register(Size)
class SizeAdmin(ExcludeBaseFieldsMixin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Gender)
class GenderAdmin(ExcludeBaseFieldsMixin):
    list_display = ('name',)
    search_fields = ('name',)
    exclude_base_fields = ('name',)


@admin.register(ProductImage)
class ProductImageAdmin(ExcludeBaseFieldsMixin, NestedModelAdmin):
    list_display = ('image',)


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 0
    fields = ('product', 'image', 'color')


@admin.register(Color)
class ColorAdmin(ExcludeBaseFieldsMixin, TranslationAdmin):
    list_display = ('name', 'hex_code')
    search_fields = ('name',)
    exclude_base_fields = ('name',)


@admin.register(Tag)
class TagAdmin(ExcludeBaseFieldsMixin, TranslationAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    exclude_base_fields = ('name',)


class ProductSizeInline(TabularInline):
    model = ProductSize
    form = ProductSizeForm
    extra = 0



class CharacteristicInline(TabularInline, NestedTabularInline):
    model = Characteristic
    extra = 0
    exclude = ['name', 'value']


class ReviewInline(TabularInline):
    model = Review
    extra = 0


@admin.register(Category)
class CategoryAdmin(ModelAdmin, DraggableMPTTAdmin, TabbedTranslationAdmin):
    search_fields = ('name',)
    exclude_base_fields = ('name', 'description')

    def indented_title(self, obj):
        return format_html(
            '<div style="text-indent:{}px;">{}</div>',
            obj.level * 20,  # Увеличивайте значение для большего отступа
            obj.name
        )
    indented_title.short_description = 'Название'

    list_display = ('tree_actions', 'indented_title', 'order',)
    list_filter = ('parent', 'name')
    mptt_level_indent = 20


@admin.register(Product)
class ProductAdmin(SortableAdminMixin, ExcludeBaseFieldsMixin, TranslationAdmin):
    form = ProductAdminForm
    list_display = ('order', 'name', 'category', 'description', 'is_active')
    search_fields = ('name',)
    list_filter = ('category',)
    filter_horizontal = ('tags',)  # 'ingredients')
    inlines = [ProductSizeInline, ProductImageInline, CharacteristicInline, ReviewInline]
    exclude_base_fields = ('name', 'description')


@admin.register(Topping)
class ToppingAdmin(ExcludeBaseFieldsMixin, TranslationAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)
    exclude_base_fields = ('name',)


@admin.register(Country)
class ToppingAdmin(ExcludeBaseFieldsMixin, TranslationAdmin):
    list_display = ('name', 'logo')
    search_fields = ('name',)
    exclude_base_fields = ('name',)
