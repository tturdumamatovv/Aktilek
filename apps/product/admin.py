from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin, messages
from modeltranslation.admin import TranslationAdmin
from unfold.admin import TabularInline, ModelAdmin

from mptt.admin import DraggableMPTTAdmin
from django.utils.html import format_html
from django.db import transaction
from django.utils.translation import gettext_lazy as _
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
    TagAdminForm, ProductImageInlineForm


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
    form = ProductImageInlineForm
    extra = 0
    fields = ('product', 'image', 'color')


@admin.register(Color)
class ColorAdmin(ExcludeBaseFieldsMixin, TabbedTranslationAdmin):
    form = ColorAdminForm
    list_display = ('name', 'color_display', 'hex_code')
    search_fields = ('name',)
    exclude_base_fields = ('name',)

    def color_display(self, obj):
        return format_html(
            '<div style="width: 200px; height: 20px; background-color: {}; border-radius: 10px;"></div>',
            obj.hex_code
        )


    color_display.short_description = 'Цвет'


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
    list_display = ('order', 'name', 'category', 'description', 'is_active', 'datetime', 'created_by')
    search_fields = ('name',)
    list_filter = ('category', 'created_by')
    filter_horizontal = ('tags', 'similar_products')  # 'ingredients')
    inlines = [ProductSizeInline, ProductImageInline, CharacteristicInline, ReviewInline]
    exclude_base_fields = ('name', 'description')
    exclude = ('slug',)
    readonly_fields = ('article', 'created_by')

    def save_model(self, request, obj, form, change):
        """Устанавливаем текущего пользователя как создателя продукта."""
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


    def save_related(self, request, form, formsets, change):
        # Сохраняем все объекты в транзакции, чтобы можно было отменить при необходимости
        with transaction.atomic():
            super().save_related(request, form, formsets, change)

            product = form.instance

            if not product.created_by:
                product.created_by = request.user
                product.save()

            # Проверка наличия изображений для каждого цвета в вариантах продукта
            color_images = {}
            for image in product.product_images.all():
                color = image.color
                if color:
                    if color in color_images:
                        color_images[color].append(image)
                    else:
                        color_images[color] = [image]

            missing_images = []
            for product_size in product.product_sizes.all():
                color = product_size.color
                if color not in color_images:
                    missing_images.append(color.name)

            # Если есть цвета без изображений, показываем ошибку и отменяем транзакцию
            if missing_images:
                messages.error(
                    request,
                    _("Для следующих цветов должны быть загружены хотя бы одно изображение: %(colors)s.") % {
                        'colors': ', '.join(missing_images)
                    }
                )
                # Откатываем все сохраненные изменения
                transaction.set_rollback(True)


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
