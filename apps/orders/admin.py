from urllib.parse import quote

from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
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
    readonly_fields = ['product_image', 'product_size', 'size_name', 'color_name', 'quantity', 'total_amount', 'is_bonus']

    def product_image(self, obj):
        if obj.product_size and obj.product_size.product.photo:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.product_size.product.photo.url)
        return "Нету фотографии"

    product_image.short_description = "Изображение продукта"
    list_per_page = 10

    def display_size_name(self, obj):
        return obj.size_name if obj.size_name else "Размер не указан"

    def display_color_name(self, obj):
        return obj.color_name if obj.color_name else "Цвет не указан"

    display_size_name.short_description = "Название размера"
    display_color_name.short_description = "Название цвета"
    list_per_page = 10


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = (
        'order_read_status', 'id', 'order_time', 'total_amount', 'link_to_user', 'order_status', 'is_pickup',
    )
    search_fields = ('user__phone_number',)
    ordering = ('-order_time',)
    list_filter = ('order_time', 'order_status', 'is_pickup', 'is_read')
    list_display_links = ('id',)
    list_editable = ('order_status',)
    readonly_fields = ('user', 'order_source', 'id', "is_read",)
    inlines = [OrderItemInline]

    def total_amount(self, obj):
        return obj.get_total_amount()

    total_amount.short_description = 'Общая сумма'

    def link_to_user(self, obj):
        return format_html('<a href="{}">{}</a>', obj.user.get_admin_url() if obj.user else '', obj.user)

    link_to_user.short_description = 'Пользователь'
    list_per_page = 10

    def order_read_status(self, obj):
        if obj.is_read:
            return format_html(
                '<div style="display: flex; align-items: center; justify-content: center; width: 24px; height: 24px;"><div class="no-animation" /></div>'
            )
        else:
            return format_html(
                '<div style="display: flex; align-items: center; justify-content: center; width: 24px; height: 24px; position: relative;"><div class="no-animation-red" /> <div class="animate-ping" /></div>'
            )

    order_read_status.short_description = "👁️"

    def change_view(self, request, object_id, form_url="", extra_context=None):
        obj = self.get_object(request, object_id)
        if obj and not obj.is_read:
            obj.is_read = True
            obj.save()
            messages.info(request, "Заказ отмечен как прочитанный.")
        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )


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
    ordering = ('active',)
    search_fields = ['code']
    list_per_page = 10



@admin.register(Warehouse)
class WarehouseAdmin(ModelAdmin):
    list_display = ['city']
    list_filter = ['city']
    search_fields = ['city']
    exclude = ['apartment_number', 'entrance', 'floor',
               'intercom', 'latitude', 'is_primary', 'longitude',
               'comment']
    list_per_page = 10
    ordering = ('city',)
