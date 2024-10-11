from modeltranslation.translator import register, TranslationOptions
from .models import (
    Category,
    Product,
    Topping,
    Size,
    Tag,
    Attribute,
    AttributeField,
    FormVariant,
    Color,
    FormCategory,
    Form,
    Ornament, FormColor
)  # Set,Ingredient


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(Topping)
class ToppingTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Size)
class SizeTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(Tag)
class TagTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Attribute)
class AttributeTranslationOptions(TranslationOptions):
    fields = ('type',)


@register(AttributeField)
class AttributeFieldTranslationOptions(TranslationOptions):
    fields = ('name',)


# @register(FormVariant)
# class FormVariantTranslationOptions(TranslationOptions):
#     fields = ('name',)

@register(Form)
class FormTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Color)
class ColorTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(FormColor)
class ColorTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Ornament)
class OrnamentTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(FormCategory)
class FormCategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


# @register(Ingredient)
# class IngredientTranslationOptions(TranslationOptions):
#     fields = ('name',)


# @register(Set)
# class SetTranslationOptions(TranslationOptions):
#     fields = ('name', 'description')
