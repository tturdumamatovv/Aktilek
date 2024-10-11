from django.apps import AppConfig


class SupportAdminChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.support_admin_chat'

    class Meta:
        verbose_name = "Поддержка"
        verbose_name_plural = "Поддержка"
