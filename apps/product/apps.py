from django.apps import AppConfig


class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.product'

    def ready(self):
        import apps.product.signals

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
