from django.apps import AppConfig


class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.product'

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
