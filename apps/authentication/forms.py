from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Permission
from django.utils.translation import gettext_lazy as _
from .models import User


class CustomPermissionSelectMultiple(forms.SelectMultiple):
    """
    Кастомный виджет для отображения разрешений с переводом.
    """
    def render(self, name, value, attrs=None, renderer=None):
        if not attrs:
            attrs = {}
        attrs['size'] = 10  # Измените размер отображаемого списка при необходимости
        return super().render(name, value, attrs, renderer)


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('phone_number', 'full_name', 'is_staff', 'is_superuser')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('phone_number', 'full_name', 'is_staff', 'is_superuser', 'user_permissions', 'groups')
        widgets = {
            'user_permissions': CustomPermissionSelectMultiple(attrs={'class': 'select-multiple'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Переводим названия разрешений на русский язык
        self.fields['user_permissions'].label = _("Разрешения")

        # Словарь с переводами стандартных действий
        action_translations = {
            'add': 'Добавить',
            'change': 'Изменить',
            'delete': 'Удалить',
            'view': 'Просмотреть',
        }

        permissions = Permission.objects.all()
        permission_choices = []
        for perm in permissions:
            content_type_model = perm.content_type.model_class()
            if content_type_model:
                content_type_name = content_type_model._meta.verbose_name
            else:
                content_type_name = perm.content_type.name  # Используем имя ContentType, если модель отсутствует

            # Разбиваем имя разрешения и переводим действия
            codename_parts = perm.codename.split('_')
            action = action_translations.get(codename_parts[0], codename_parts[0])  # Переводим действие
            translated_name = f"{action} {content_type_name}"
            permission_choices.append((perm.id, translated_name))

        self.fields['user_permissions'].choices = permission_choices
