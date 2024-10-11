from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from unfold.admin import TabularInline, ModelAdmin, StackedInline

from mptt.admin import MPTTModelAdmin

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
    Attribute,
    AttributeField,
    Form,
    FormVariant,
    FormCategory,
    Ornament,
    FormColor,
    OrderRequest
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
class SizeAdmin(ExcludeBaseFieldsMixin, TranslationAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    exclude_base_fields = ('name', 'description')


@admin.register(Tag)
class TagAdmin(ExcludeBaseFieldsMixin, TranslationAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    exclude_base_fields = ('name',)


class ProductSizeInline(TabularInline):
    model = ProductSize
    form = ProductSizeForm
    extra = 0


class CharacteristicInline(TabularInline):
    model = Characteristic
    extra = 0


class ReviewInline(TabularInline):
    model = Review
    extra = 0


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ('name', 'parent', 'order')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}  # автоматически генерируем слаг по названию
    mptt_level_indent = 20


@admin.register(Product)
class ProductAdmin(SortableAdminMixin, ExcludeBaseFieldsMixin, TranslationAdmin):
    form = ProductAdminForm
    list_display = ('order', 'name', 'category', 'description')
    search_fields = ('name',)
    list_filter = ('category',)
    filter_horizontal = ('toppings', 'tags',)  # 'ingredients')
    inlines = [ProductSizeInline, CharacteristicInline, ReviewInline]
    exclude_base_fields = ('name', 'description')


@admin.register(Topping)
class ToppingAdmin(ExcludeBaseFieldsMixin, TranslationAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)
    exclude_base_fields = ('name',)


class AttributeFieldInline(TabularInline):
    model = AttributeField
    extra = 0


# Админка для Form
@admin.register(Form)
class FormAdmin(ModelAdmin, TranslationAdmin):
    list_display = ('name', 'category')
    filter_horizontal = ['ornaments', 'form_color', 'attribute']
    # inlines = [OrnamentInline, FormColorInline, AttributeInline]

# Админка для FormCategory
@admin.register(FormCategory)
class FormCategoryAdmin(ModelAdmin, TranslationAdmin):
    list_display = ('name', 'description')

# Админка для Ornament
@admin.register(Ornament)
class OrnamentAdmin(ModelAdmin, TranslationAdmin):
    list_display = ('name',)
    exclude = ('form',)  # Так как у нас есть через промежуточную таблицу, убираем основное поле

# Админка для FormColor
@admin.register(FormColor)
class FormColorAdmin(ModelAdmin, TranslationAdmin):
    list_display = ('name', 'hex_code')
    exclude = ('form',)  # Тоже убираем из админки ManyToMany поле

# Админка для Attribute
@admin.register(Attribute)
class AttributeAdmin(ModelAdmin, TranslationAdmin):
    list_display = ('type',)
    exclude = ('form',)
    inlines = [AttributeFieldInline]

# Админка для FormVariant
@admin.register(FormVariant)
class FormVariantAdmin(ModelAdmin):
    list_display = ('name', 'color', 'ornament', 'form')
    filter_horizontal = ('attribute_fields',)

# Админка для AttributeField
@admin.register(AttributeField)
class AttributeFieldAdmin(ModelAdmin, TranslationAdmin):
    list_display = ('name', 'attribute')


@admin.register(OrderRequest)
class OrderRequestAdmin(ModelAdmin):
    list_display = ('full_name', 'phone_number')
