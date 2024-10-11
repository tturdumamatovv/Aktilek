from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import TabularInline, ModelAdmin

from .models import User, UserAddress
from apps.orders.models import Order


class OrderInline(TabularInline):
    model = Order
    extra = 0
    classes = ['collapse']
    fields = (
        'restaurant',
        'delivery',
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
            'restaurant',
            'delivery',
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
class UserAddressAdmin(admin.ModelAdmin):
    pass


class UserAddressInline(admin.StackedInline):
    model = UserAddress
    extra = 0
    classes = ['collapse']


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ('phone_number', 'full_name', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser',)
    fieldsets = (
        (None, {'fields': ('phone_number', 'full_name')}),
        (_('Personal info'), {'fields': ('date_of_birth', 'email', 'profile_picture', 'bonus'),
                              'classes': ('collapse',)
                              }),
        (_('Permissions'), {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_order', 'receive_notifications',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2'),
        }),
    )
    search_fields = ('phone_number', 'full_name')
    ordering = ('phone_number',)
    filter_horizontal = ('groups', 'user_permissions',)
    inlines = [OrderInline, UserAddressInline]
