from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'

    def ready(self):
        import apps.authentication.signals

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"