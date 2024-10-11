from django.apps import AppConfig


class PagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pages'

    class Meta:
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"