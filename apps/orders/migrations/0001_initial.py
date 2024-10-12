# Generated by Django 5.0.7 on 2024-10-12 13:24

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0001_initial'),
        ('product', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DistancePricing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance', models.IntegerField(verbose_name='Расстояние (км)')),
                ('price', models.IntegerField(verbose_name='Цена')),
            ],
            options={
                'verbose_name': 'Тариф на расстояние',
                'verbose_name_plural': 'Тарифы на расстояния',
            },
        ),
        migrations.CreateModel(
            name='PercentCashback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile_percent', models.IntegerField(verbose_name='Процент за мобильное приложение')),
                ('web_percent', models.IntegerField(verbose_name='Процент за веб-сайт')),
            ],
            options={
                'verbose_name': 'Процент кэшбэка',
                'verbose_name_plural': 'Проценты кэшбэка',
            },
        ),
        migrations.CreateModel(
            name='PromoCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True, verbose_name='Промокод')),
                ('valid_from', models.DateTimeField(verbose_name='Начало действия')),
                ('valid_to', models.DateTimeField(verbose_name='Конец действия')),
                ('discount', models.IntegerField(help_text='Процент скидки', verbose_name='Скидка')),
                ('active', models.BooleanField(default=False, verbose_name='Активен')),
                ('type', models.CharField(choices=[('%', 'Процент'), ('сом', 'Фиксированная сумма')], max_length=3, verbose_name='Тип')),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='reports/', verbose_name='Картинка')),
                ('description', models.TextField(verbose_name='Описание')),
                ('contact_number', models.CharField(max_length=15, verbose_name='Контактный номер')),
            ],
            options={
                'verbose_name': 'Отчет',
                'verbose_name_plural': 'Отчеты',
            },
        ),
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('address', models.CharField(max_length=255, verbose_name='Адрес')),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True, verbose_name='Телефонный номер')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Электронная почта')),
                ('opening_hours', models.TimeField(blank=True, null=True, verbose_name='Время открытия')),
                ('closing_hours', models.TimeField(blank=True, null=True, verbose_name='Время закрытия')),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Широта')),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Долгота')),
                ('telegram_chat_ids', models.TextField(blank=True, help_text='Введите чат-айди через запятую', null=True, validators=[django.core.validators.MinLengthValidator(1)], verbose_name='Telegram Chat IDs')),
                ('self_pickup_available', models.BooleanField(default=True, verbose_name='Самовывоз доступен')),
            ],
            options={
                'verbose_name': 'Ресторан',
                'verbose_name_plural': 'Рестораны',
            },
        ),
        migrations.CreateModel(
            name='TelegramBotToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bot_token', models.CharField(max_length=200, unique=True, verbose_name='Телеграм Бот Токен')),
                ('report_channels', models.TextField(blank=True, max_length=200, null=True, verbose_name='Айди каналов')),
                ('app_download_link', models.CharField(blank=True, max_length=250, null=True, verbose_name='Ссылка на приложение')),
                ('google_map_api_key', models.CharField(blank=True, max_length=250, null=True, verbose_name='Ключ для карты')),
            ],
            options={
                'verbose_name': 'Токен бота Telegram',
                'verbose_name_plural': 'Токены бота Telegram',
            },
        ),
        migrations.CreateModel(
            name='WhatsAppChat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('whatsapp_number', models.CharField(max_length=200, unique=True, verbose_name='Телеграм Бот Токен')),
            ],
            options={
                'verbose_name': 'Номер WhatsApp',
                'verbose_name_plural': 'Номер WhatsApp',
            },
        ),
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_time', models.DateTimeField(blank=True, null=True, verbose_name='Время доставки')),
                ('delivery_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Стоимость доставки')),
                ('distance_km', models.CharField(blank=True, max_length=10, null=True, verbose_name='Расстояние (км)')),
                ('user_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='authentication.useraddress', verbose_name='Адрес пользователя')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.restaurant', verbose_name='Ресторан')),
            ],
            options={
                'verbose_name': 'Доставка',
                'verbose_name_plural': 'Доставки',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_time', models.DateTimeField(auto_now_add=True, verbose_name='Время заказа')),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Общая сумма')),
                ('total_bonus_amount', models.IntegerField(blank=True, null=True, verbose_name='Общая сумма бонусов')),
                ('is_pickup', models.BooleanField(default=False, verbose_name='Самовывоз')),
                ('payment_method', models.CharField(choices=[('card', 'Карта'), ('cash', 'Наличные'), ('online', 'Онлайн')], default='card', max_length=255, verbose_name='Способ оплаты')),
                ('change', models.IntegerField(blank=True, null=True, verbose_name='Сдача')),
                ('order_status', models.CharField(choices=[('pending', 'В ожидании'), ('in_progress', 'В процессе'), ('delivery', 'Доставка'), ('completed', 'Завершено'), ('cancelled', 'Отменено')], default='pending', max_length=20, verbose_name='Статус заказа')),
                ('order_source', models.CharField(choices=[('mobile', 'Мобильное приложение'), ('web', 'Веб-сайт'), ('unknown', 'Неизвестно')], default='unknown', max_length=10, verbose_name='Источник заказа')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Комментарий')),
                ('delivery', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.delivery', verbose_name='Доставка')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
                ('promo_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.promocode')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.restaurant', verbose_name='Ресторан')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(verbose_name='Количество')),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Общая сумма')),
                ('is_bonus', models.BooleanField(default=False, verbose_name='Бонусный продукт')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='orders.order', verbose_name='Заказ')),
                ('product_size', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='product.productsize', verbose_name='Размер продукта')),
                ('topping', models.ManyToManyField(blank=True, to='product.topping', verbose_name='Добавки')),
            ],
            options={
                'verbose_name': 'Элемент заказа',
                'verbose_name_plural': 'Элементы заказа',
            },
        ),
    ]
