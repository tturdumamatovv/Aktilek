from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.orders'

    def ready(self):
        import apps.orders.signals


    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
