import random
import string
from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.pages.models import SingletonModel
from apps.product.models import ProductSize, Topping, Size


class Order(models.Model):
    order_time = models.DateTimeField(auto_now_add=True, verbose_name=_('Время заказа'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Общая сумма'), blank=True,
                                       null=True)
    total_bonus_amount = models.IntegerField(verbose_name=_('Общая сумма бонусов'), blank=True, null=True)

    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='orders', verbose_name=_('Пользователь')
                             , blank=True, null=True)
    is_pickup = models.BooleanField(default=False, verbose_name=_('Самовывоз'))
    payment_method = models.CharField(
        max_length=255,
        choices=[('card', 'Карта'),
                 ('cash', 'Наличные'),
                 ('online', 'Онлайн')],
        default='card',
        verbose_name=_('Способ оплаты')
    )
    change = models.IntegerField(verbose_name=_('Сдача'), blank=True, null=True)

    order_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', _('В ожидании')),
            ('in_progress', _('В процессе')),
            ('delivery', _('Доставка')),
            ('completed', _('Завершено')),
            ('cancelled', _('Отменено'))
        ],
        default='pending',
        verbose_name=_('Статус заказа')
    )
    order_source = models.CharField(
        max_length=10,
        choices=[
            ('mobile', 'Мобильное приложение'),
            ('web', 'Веб-сайт'),
            ('unknown', 'Неизвестно')
        ],
        default='unknown',
        verbose_name=_('Источник заказа')
    )
    comment = models.TextField(verbose_name=_('Комментарий'), blank=True, null=True)
    promo_code = models.ForeignKey('PromoCode', on_delete=models.SET_NULL, null=True, blank=True)
    user_address = models.ForeignKey('authentication.UserAddress', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")

    def __str__(self):
        return f"Заказ #{self.id}"

    def apply_promo_code(self):
        discount_amount = Decimal(0)  # Инициализируем переменную

        if self.promo_code and self.promo_code.is_valid():
            if self.promo_code.type == 'p':
                # Если тип промокода процентный, рассчитываем процентную скидку
                discount_rate = Decimal(self.promo_code.discount) / Decimal(100)
                discount_amount = discount_rate * self.total_amount
            elif self.promo_code.type == 'f':
                # Если тип промокода фиксированная сумма, берем фиксированную скидку
                discount_amount = Decimal(self.promo_code.discount)

            # Убедитесь, что скидка не превышает общую сумму
            discount_amount = min(discount_amount, self.total_amount)

        return self.total_amount - discount_amount

    def get_total_amount(self):
        total_amount = Decimal(0)
        for order_item in self.order_items.all():
            total_amount += order_item.total_amount
        return total_amount

    def get_total_bonus_amount(self):
        total_bonus_amount = self.total_bonus_amount or 0
        for order_item in self.order_items.filter(is_bonus=True):
            total_bonus_amount += order_item.total_amount
        return total_bonus_amount

    def save(self, *args, **kwargs):
        self.total_amount = self.apply_promo_code()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items', verbose_name=_('Заказ'))
    product_size = models.ForeignKey(ProductSize, on_delete=models.CASCADE, verbose_name=_('Размер продукта'),
                                     blank=True, null=True)
    size_id = models.IntegerField(verbose_name=_('Выбранный размер'), blank=True, null=True)
    size_name = models.CharField(max_length=255, verbose_name=_('Размер'), blank=True, null=True)
    color_id = models.IntegerField(verbose_name=_('Выбранный цвет'), blank=True, null=True)
    color_name = models.CharField(max_length=100, verbose_name=_('Название цвета'), blank=True, null=True)
    quantity = models.PositiveIntegerField(verbose_name=_('Количество'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Общая сумма'))
    is_bonus = models.BooleanField(default=False, verbose_name=_('Бонусный продукт'))

    class Meta:
        verbose_name = _("Элемент заказа")
        verbose_name_plural = _("Элементы заказа")

    def __str__(self):
        if self.product_size:
            return f"{self.product_size.product.name} - {self.size_name if self.size_name else 'Размер не указан'} - {self.quantity} шт."
        return f"Товар - {self.size_name if self.size_name else 'Размер не указан'} - {self.quantity} шт."

    def calculate_total_amount(self):
        if not self.is_bonus:
            product = self.product_size.product  # Получаем связанный продукт
            # Используем discounted_price, если оно есть, иначе обычную цену
            price = product.discounted_price if product.discounted_price else product.price
            total = self.quantity * price
            return total
        else:
            # Получаем бонусную цену из продукта
            total = self.quantity * self.product_size.product.bonus_price
            return total

    def save(self, *args, **kwargs):
        # Сохраняем названия размера и цвета, если есть product_size
        if self.product_size:
            self.size_name = self.product_size.size.name if self.product_size.size else "Размер не указан"
            self.size_id = self.product_size.size.id if self.product_size.size else None

            self.color_name = self.product_size.color.name if self.product_size.color else "Цвет не указан"
            self.color_id = self.product_size.color.id if self.product_size.color else None

        # Рассчитываем общую сумму
        self.total_amount = self.calculate_total_amount()

        # Сохраняем элемент заказа
        super().save(*args, **kwargs)

        # Обновляем общую сумму заказа
        self.order.total_amount = self.order.get_total_amount()

        # Если товар оплачивается бонусами, обновляем общую сумму бонусов заказа
        if self.is_bonus:
            self.order.total_bonus_amount = self.order.get_total_bonus_amount()

        # Сохраняем изменения в заказе
        self.order.save()

class PercentCashback(SingletonModel):
    mobile_percent = models.IntegerField(verbose_name=_("Процент за мобильное приложение"))
    web_percent = models.IntegerField(verbose_name=_("Процент за веб-сайт"))
    min_order_price = models.IntegerField(verbose_name=_("Минимальная сумма заказа"))

    def __str__(self):
        return f"Процент кэшбека № {self.id}"

    class Meta:
        verbose_name = _("Процент кэшбэка")
        verbose_name_plural = _("Проценты кэшбэка")


class Report(models.Model):
    image = models.ImageField(upload_to='reports/', blank=True, null=True, verbose_name=_("Картинка"))
    description = models.TextField(verbose_name=_("Описание"))
    contact_number = models.CharField(max_length=15, verbose_name=_("Контактный номер"))

    def __str__(self):
        return f"Отчет № {self.id}"

    class Meta:
        verbose_name = _("Отчет")
        verbose_name_plural = _("Отчеты")


class PromoCode(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name='Промокод')
    valid_from = models.DateTimeField(verbose_name='Начало действия')
    valid_to = models.DateTimeField(verbose_name='Конец действия')
    discount = models.IntegerField(help_text='Процент скидки', verbose_name='Скидка')
    active = models.BooleanField(default=False, verbose_name='Активен')
    type = models.CharField(max_length=3, choices=[('%', 'Процент'), ('сом', 'Фиксированная сумма')], verbose_name='Тип')

    def __str__(self):
        return self.code

    @staticmethod
    def generate_code(length=6):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

    def is_valid(self):
        from django.utils import timezone
        return self.active and self.valid_from <= timezone.now() <= self.valid_to


class Warehouse(models.Model):
    city = models.CharField(max_length=100, verbose_name=_("Адрес"), null=True, blank=True)
    apartment_number = models.CharField(max_length=10, verbose_name=_("Номер квартиры"), null=True, blank=True)
    entrance = models.CharField(max_length=10, verbose_name=_("Подъезд"), null=True, blank=True)
    floor = models.CharField(max_length=10, verbose_name=_("Этаж"), null=True, blank=True)
    intercom = models.CharField(max_length=10, verbose_name=_("Домофон"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    is_primary = models.BooleanField(default=False, verbose_name=_("Главный"))
    latitude = models.DecimalField(max_digits=200, decimal_places=6, verbose_name=_('Широта'), null=True, blank=True)
    longitude = models.DecimalField(max_digits=200, decimal_places=6, verbose_name=_('Долгота'), null=True, blank=True)
    comment = models.TextField(verbose_name=_("Комментарий"), null=True, blank=True)

    class Meta:

        verbose_name = _("Склад")
        verbose_name_plural = _("Склады")
