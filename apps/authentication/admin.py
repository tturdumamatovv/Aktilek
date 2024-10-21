from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import TabularInline, ModelAdmin, StackedInline
from django.contrib.auth.models import Permission

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User, UserAddress
from apps.orders.models import Order


class OrderInline(TabularInline):
    model = Order
    extra = 0
    classes = ['collapse']
    fields = (
        'order_time',
        'total_amount',
        'total_bonus_amount',
        'user',
        'is_pickup',
        'payment_method',
        'change',
        'order_status',
        'order_source',
        'comment',
    )
    readonly_fields = (
            'order_time',
            'total_amount',
            'total_bonus_amount',
            'user',
            'is_pickup',
            'payment_method',
            'change',
            'order_status',
            'order_source',
            'comment',
    )


@admin.register(UserAddress)
class UserAddressAdmin(ModelAdmin):
    pass


class UserAddressInline(StackedInline):
    model = UserAddress
    extra = 0
    classes = ['collapse']


@admin.register(User)
class UserAdmin(ModelAdmin):
    add_form = CustomUserCreationForm  # Используем форму для создания пользователя
    form = CustomUserChangeForm  # Используем форму для редактирования пользователя

    list_display = ('phone_number', 'full_name', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser',)

    fieldsets = (
        (None, {'fields': ('phone_number', 'full_name', 'password')}),
        ('Personal info', {'fields': ('date_of_birth', 'email', 'profile_picture', 'bonus'),
                           'classes': ('collapse',)}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        # Добавляем user_permissions
        ('Important dates', {'fields': ('last_order', 'receive_notifications',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'full_name', 'password1', 'password2', 'is_staff', 'is_superuser'),
            # Добавляем password1 и password2
        }),
    )

    search_fields = ('phone_number', 'full_name')
    ordering = ('phone_number',)
    filter_horizontal = ('groups', 'user_permissions')
    list_editable = ('is_staff', 'is_superuser')

    def get_form(self, request, obj=None, **kwargs):
        """
        Используем нужную форму для создания или изменения пользователя.
        """
        if obj is None:  # Создание пользователя
            kwargs['form'] = self.add_form
        else:  # Редактирование пользователя
            kwargs['form'] = self.form
        return super().get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)

        if obj and obj.is_staff:
            # Добавляем поле с выбором разрешений, если пользователь - работник
            additional_permissions = ('Дополнительные разрешения', {'fields': ('user_permissions',)})
            fieldsets = fieldsets + (additional_permissions,)

        return fieldsets
