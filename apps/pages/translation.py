from modeltranslation.translator import register, TranslationOptions
from .models import StaticPage, Redirection, MethodsOfPayment


@register(StaticPage)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(Redirection)
class RedirectionTranslationOption(TranslationOptions):
    fields = ('title', 'description')


@register(MethodsOfPayment)
class MethodsOfPaymentTranslationOption(TranslationOptions):
    fields = ('title', 'description')
