from urllib.parse import quote

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline

from .models import (
    Restaurant,
    Delivery,
    Order,
    OrderItem,
    DistancePricing,
    TelegramBotToken,
    PercentCashback,
    Report, WhatsAppChat, PromoCode
)
from apps.services.generate_message import generate_order_message


@admin.register(TelegramBotToken)
class TelegramBotTokenAdmin(ModelAdmin):
    pass


@admin.register(WhatsAppChat)
class WhatsAppChatAdmin(ModelAdmin):
    pass


@admin.register(Restaurant)
class RestaurantAdmin(ModelAdmin):
    list_display = ('name', 'address', 'phone_number', 'email', 'opening_hours')
    search_fields = ('name', 'address')
    list_filter = ('opening_hours',)


@admin.register(Delivery)
class DeliveryAdmin(ModelAdmin):
    list_display = ('restaurant', 'user_address', 'delivery_time', 'delivery_fee')
    search_fields = ('restaurant__name', 'user_address__city')
    list_filter = ('delivery_time', 'restaurant')


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = (
        'id', 'restaurant', 'delivery', 'order_time', 'total_amount', 'link_to_user', 'order_status', 'is_pickup',
        'order_request_button')
    search_fields = ('user__phone_number',)
    list_filter = ('order_time', 'order_status', 'restaurant', 'is_pickup')
    list_display_links = ('id',)
    list_editable = ('order_status',)
    readonly_fields = ('user', 'delivery', 'order_source', 'id',)
    inlines = [OrderItemInline]

    def total_amount(self, obj):
        return obj.get_total_amount()

    total_amount.short_description = 'Общая сумма'

    def link_to_user(self, obj):
        # return 1
        return format_html('<a href="{}">{}</a>', obj.user.get_admin_url() if obj.user else '', obj.user)

    link_to_user.short_description = 'Пользователь'

    def order_request_button(self, obj):
        # Инициализация переменной с пустой строкой
        url_encoded_message = ''

        # Получаем расстояние и стоимость доставки, если они доступны
        distance = obj.delivery.distance_km if obj.delivery else None
        delivery_fee = obj.delivery.delivery_fee if obj.delivery else None

        # Генерируем сообщение, если есть доставка и стоимость
        if distance and delivery_fee:
            message = generate_order_message(obj, distance, delivery_fee)
            url_encoded_message = quote(message)  # Кодируем сообщение для URL

        # Получаем номер WhatsApp, если он существует
        phone = WhatsAppChat.objects.first()
        if not phone:
            return format_html('')

        # Создаём ссылку на WhatsApp
        link = f'https://wa.me/{phone.whatsapp_number}?text={url_encoded_message}'
        return format_html(
            f'<a style="color: white; background-color: orange;" class="button" target="_blank" href="{link}">WhatsApp</a>'
        )

    order_request_button.short_description = 'Действие'


@admin.register(DistancePricing)
class DistancePricingInline(ModelAdmin):
    pass


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


