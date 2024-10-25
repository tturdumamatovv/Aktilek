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
    warehouse = models.ForeignKey('Warehouse', null=True, blank=True, on_delete=models.SET_NULL, related_name='orders')
    is_read = models.BooleanField(default=False, verbose_name=_("Прочитано"))

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")

    def __str__(self):
        return f"Заказ #{self.id}"

    def apply_promo_code(self):
        discount_amount = Decimal(0)  # Инициализируем переменную
        print(f"Applying promo code, current total amount: {self.total_amount}")

        # Убедимся, что сумма заказа не None
        if self.total_amount is None:
            self.total_amount = Decimal(0)

        if self.promo_code and self.promo_code.is_valid():
            print(f"Promo code: {self.promo_code.code}")

            # Применение процентного промо-кода
            if self.promo_code.type == '%':
                discount_rate = Decimal(self.promo_code.discount) / Decimal(100)
                discount_amount = discount_rate * self.total_amount
                print(f"Discount rate: {discount_rate}, Discount amount: {discount_amount}")

            # Применение фиксированного промо-кода (сом)
            elif self.promo_code.type == 'сом':
                discount_amount = Decimal(self.promo_code.discount)
                print(f"Fixed discount amount: {discount_amount}")

            # Убедимся, что сумма скидки не превышает общую сумму заказа
            discount_amount = min(discount_amount, self.total_amount)
            print(f"Final discount amount applied: {discount_amount}")

        # Вычитаем скидку из общей суммы
        new_total_amount = self.total_amount - discount_amount
        print(f"Total amount after applying promo code: {new_total_amount}")

        return new_total_amount

    def get_total_amount(self):
        total_amount = Decimal(0)
        # Calculate total amount based on ProductSize prices
        for order_item in self.order_items.all():
            product_size = order_item.product_size
            if order_item.is_bonus and product_size.bonus_price is not None:
                total_amount += product_size.bonus_price * order_item.quantity
            elif product_size.discounted_price is not None:
                total_amount += product_size.discounted_price * order_item.quantity
            else:
                total_amount += product_size.price * order_item.quantity
        return total_amount

    def get_total_bonus_amount(self):
        total_bonus_amount = self.total_bonus_amount or 0
        # Calculate total bonus amount based on ProductSize bonus_price
        for order_item in self.order_items.filter(is_bonus=True):
            product_size = order_item.product_size
            total_bonus_amount += product_size.bonus_price * order_item.quantity
        return total_bonus_amount

    def apply_bonuses(self):
        from apps.services.bonuces import calculate_bonus_points, apply_bonus_points
        # Логика для начисления бонусов, если заказ завершен
        if not self.total_bonus_amount and not any(item.is_bonus for item in self.order_items.all()):
            bonus_points = calculate_bonus_points(self.total_amount, 0, self.order_source)
            self.total_bonus_amount = bonus_points  # Сохраняем бонусы в заказе
            apply_bonus_points(self.user, bonus_points)
            self.save()

    def save(self, *args, **kwargs):
        # Применяем промо-код только если общая сумма не была ранее уменьшена
        if not self.total_amount or self.total_amount == self.get_total_amount():
            print(f"Applying promo code, current total amount: {self.total_amount}")
            self.total_amount = self.apply_promo_code()
            print(f"Total amount after applying promo code: {self.total_amount}")

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
    is_ordered = models.BooleanField(default=False, verbose_name='Заказан')

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
