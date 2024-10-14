from modeltranslation.translator import register, TranslationOptions
from .models import (
    Category,
    Product,
    Topping,
    Tag,
    Color,
    Country,
    Gender,
    Characteristic
)  # Set,Ingredient


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(Characteristic)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'value')


@register(Country)
class CountryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Gender)
class GenderTranslationOptions(TranslationOptions):
    fields = ('name',)



@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(Topping)
class ToppingTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Tag)
class TagTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Color)
class ColorTranslationOptions(TranslationOptions):
    fields = ('name',)


# @register(Ingredient)
# class IngredientTranslationOptions(TranslationOptions):
#     fields = ('name',)


# @register(Set)
# class SetTranslationOptions(TranslationOptions):
#     fields = ('name', 'description')
