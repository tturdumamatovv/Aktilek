from urllib.parse import quote

from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline

from .models import (
    Order,
    OrderItem,
    PercentCashback,
    Report,
    PromoCode, Warehouse
)
from apps.services.generate_message import generate_order_message


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    exclude = ['size_id', 'color_id']
    readonly_fields = ['product_size', 'size_name', 'color_name', 'quantity', 'total_amount', 'is_bonus']

    def display_size_name(self, obj):
        return obj.size_name if obj.size_name else "Размер не указан"

    def display_color_name(self, obj):
        return obj.color_name if obj.color_name else "Цвет не указан"

    display_size_name.short_description = "Название размера"
    display_color_name.short_description = "Название цвета"


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = (
        'id', 'order_time', 'total_amount', 'link_to_user', 'order_status', 'is_pickup',
    )
    search_fields = ('user__phone_number',)
    list_filter = ('order_time', 'order_status', 'is_pickup')
    list_display_links = ('id',)
    list_editable = ('order_status',)
    readonly_fields = ('user', 'order_source', 'id',)
    inlines = [OrderItemInline]

    def total_amount(self, obj):
        return obj.get_total_amount()

    total_amount.short_description = 'Общая сумма'

    def link_to_user(self, obj):
        return format_html('<a href="{}">{}</a>', obj.user.get_admin_url() if obj.user else '', obj.user)

    link_to_user.short_description = 'Пользователь'


@admin.register(PercentCashback)
class PercentCashbackAdmin(ModelAdmin):
    pass


@admin.register(Report)
class ReportAdmin(ModelAdmin):
    pass


@admin.register(PromoCode)
class PromoCodeAdmin(ModelAdmin):
    list_display = ['code', 'discount', 'valid_from', 'valid_to', 'active', 'type']
    list_filter = ['active', 'valid_from', 'valid_to']
    search_fields = ['code']


@admin.register(Warehouse)
class WarehouseAdmin(ModelAdmin):
    list_display = ['city']
    list_filter = ['city']
    search_fields = ['city']
