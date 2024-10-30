from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from unfold.admin import TabularInline, ModelAdmin

from mptt.admin import DraggableMPTTAdmin
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline

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
    Gender, SizeChart
)
from .forms import ProductSizeForm, ProductAdminForm, CharacteristicInlineForm, CategoryAdminForm, ColorAdminForm, \
    TagAdminForm


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
class ProductImageAdmin(ExcludeBaseFieldsMixin):
    list_display = ('image',)


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 0
    fields = ('product', 'image', 'color')


@admin.register(Color)
class ColorAdmin(ExcludeBaseFieldsMixin, TabbedTranslationAdmin):
    form = ColorAdminForm
    list_display = ('name', 'hex_code')
    search_fields = ('name',)
    exclude_base_fields = ('name',)


@admin.register(Tag)
class TagAdmin(ExcludeBaseFieldsMixin, TabbedTranslationAdmin):
    form = TagAdminForm
    list_display = ('name',)
    search_fields = ('name',)
    exclude_base_fields = ('name',)


class ProductSizeInline(TabularInline):
    model = ProductSize
    form = ProductSizeForm
    extra = 0


class CharacteristicInline(TabularInline, TranslationTabularInline):
    model = Characteristic
    extra = 0


class ReviewInline(TabularInline):
    model = Review
    extra = 0


@admin.register(Category)
class CategoryAdmin(ModelAdmin, DraggableMPTTAdmin, TabbedTranslationAdmin):
    form = CategoryAdminForm
    search_fields = ('name',)
    exclude_base_fields = ('name', 'description')
    exclude = ('slug',)

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
class ProductAdmin(ModelAdmin, SortableAdminMixin, TabbedTranslationAdmin):
    form = ProductAdminForm
    list_display = ('order', 'name', 'category', 'description', 'is_active', 'datetime')
    search_fields = ('name',)
    list_filter = ('category',)
    filter_horizontal = ('tags', 'similar_products')  # 'ingredients')
    inlines = [ProductSizeInline, ProductImageInline, CharacteristicInline, ReviewInline]
    exclude_base_fields = ('name', 'description')
    exclude = ('slug',)


@admin.register(Topping)
class ToppingAdmin(ExcludeBaseFieldsMixin, TranslationAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)
    exclude_base_fields = ('name',)


@admin.register(SizeChart)
class SizeChartAdmin(ExcludeBaseFieldsMixin):
    list_display = ('name', 'image')
    search_fields = ('name',)


@admin.register(Country)
class ToppingAdmin(ExcludeBaseFieldsMixin, TranslationAdmin):
    list_display = ('name', 'logo')
    search_fields = ('name',)
    exclude_base_fields = ('name',)
