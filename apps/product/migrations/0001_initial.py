# Generated by Django 5.0.7 on 2024-10-12 14:26

import colorfield.fields
import django.db.models.deletion
import mptt.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(blank=True, max_length=255, null=True, verbose_name='Тип')),
                ('type_ru', models.CharField(blank=True, max_length=255, null=True, verbose_name='Тип')),
                ('type_en', models.CharField(blank=True, max_length=255, null=True, verbose_name='Тип')),
                ('type_ky', models.CharField(blank=True, max_length=255, null=True, verbose_name='Тип')),
            ],
            options={
                'verbose_name': 'Аттрибут',
                'verbose_name_plural': 'Аттрибуты',
            },
        ),
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Цвет')),
                ('name_ru', models.CharField(max_length=50, null=True, verbose_name='Цвет')),
                ('name_en', models.CharField(max_length=50, null=True, verbose_name='Цвет')),
                ('name_ky', models.CharField(max_length=50, null=True, verbose_name='Цвет')),
                ('hex_code', colorfield.fields.ColorField(default='#FFFFFF', image_field=None, max_length=25, samples=None, verbose_name='HEX Код')),
            ],
            options={
                'verbose_name': 'Цвет',
                'verbose_name_plural': 'Цвета',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Страна')),
                ('name_ru', models.CharField(max_length=255, null=True, verbose_name='Страна')),
                ('name_en', models.CharField(max_length=255, null=True, verbose_name='Страна')),
                ('name_ky', models.CharField(max_length=255, null=True, verbose_name='Страна')),
                ('logo', models.FileField(upload_to='countries', verbose_name='Флаг Страны')),
            ],
            options={
                'verbose_name': 'Страна',
                'verbose_name_plural': 'Страны',
            },
        ),
        migrations.CreateModel(
            name='FormCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('name_ru', models.CharField(max_length=255, null=True, verbose_name='Название')),
                ('name_en', models.CharField(max_length=255, null=True, verbose_name='Название')),
                ('name_ky', models.CharField(max_length=255, null=True, verbose_name='Название')),
                ('description', models.CharField(blank=True, max_length=255, verbose_name='Описание')),
                ('description_ru', models.CharField(blank=True, max_length=255, null=True, verbose_name='Описание')),
                ('description_en', models.CharField(blank=True, max_length=255, null=True, verbose_name='Описание')),
                ('description_ky', models.CharField(blank=True, max_length=255, null=True, verbose_name='Описание')),
                ('slug', models.SlugField(blank=True, max_length=100, null=True, unique=True, verbose_name='Ссылка')),
            ],
            options={
                'verbose_name': 'Категория формы',
                'verbose_name_plural': 'Категории форм',
            },
        ),
        migrations.CreateModel(
            name='FormColor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Цвет')),
                ('name_ru', models.CharField(max_length=50, null=True, verbose_name='Цвет')),
                ('name_en', models.CharField(max_length=50, null=True, verbose_name='Цвет')),
                ('name_ky', models.CharField(max_length=50, null=True, verbose_name='Цвет')),
                ('hex_code', colorfield.fields.ColorField(default='#FFFFFF', image_field=None, max_length=25, samples=None, verbose_name='HEX Код')),
            ],
            options={
                'verbose_name': 'Цвет Формы',
                'verbose_name_plural': 'Цвета для Форм',
            },
        ),
        migrations.CreateModel(
            name='Gender',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Гендер')),
                ('name_ru', models.CharField(max_length=255, null=True, verbose_name='Гендер')),
                ('name_en', models.CharField(max_length=255, null=True, verbose_name='Гендер')),
                ('name_ky', models.CharField(max_length=255, null=True, verbose_name='Гендер')),
            ],
            options={
                'verbose_name': 'Пол',
                'verbose_name_plural': 'Пол',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='topping_photos/', verbose_name='Фото')),
                ('possibly_remove', models.BooleanField(default=False, verbose_name='Возможность удаления')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
            },
        ),
        migrations.CreateModel(
            name='OrderRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255, verbose_name='Имя Фамилия')),
                ('email', models.EmailField(max_length=254, verbose_name='Электронная почта')),
                ('phone_number', models.CharField(max_length=20, verbose_name='Номер для связи')),
                ('city_region', models.CharField(max_length=255, verbose_name='Город/регион')),
                ('quantity', models.IntegerField(verbose_name='Предполагаемое количество единиц')),
                ('delivery_date', models.DateField(verbose_name='Когда требуется заказ?')),
                ('comments', models.TextField(blank=True, null=True, verbose_name='Ваш комментарий')),
            ],
            options={
                'verbose_name': 'Заявка',
                'verbose_name_plural': 'Заявки',
            },
        ),
        migrations.CreateModel(
            name='Ornament',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Название')),
                ('name_ru', models.CharField(blank=True, max_length=255, null=True, verbose_name='Название')),
                ('name_en', models.CharField(blank=True, max_length=255, null=True, verbose_name='Название')),
                ('name_ky', models.CharField(blank=True, max_length=255, null=True, verbose_name='Название')),
                ('image', models.FileField(blank=True, max_length=500, null=True, upload_to='ornament', verbose_name='Орнамент')),
            ],
            options={
                'verbose_name': 'Орнамент',
                'verbose_name_plural': 'Орнаменты',
            },
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Размер',
                'verbose_name_plural': 'Размеры',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('name_ru', models.CharField(max_length=100, null=True, verbose_name='Название')),
                ('name_en', models.CharField(max_length=100, null=True, verbose_name='Название')),
                ('name_ky', models.CharField(max_length=100, null=True, verbose_name='Название')),
                ('text_color', colorfield.fields.ColorField(default='#FF0000', image_field=None, max_length=25, samples=None, verbose_name='Цвет текста')),
                ('background_color', colorfield.fields.ColorField(default='#FF0000', image_field=None, max_length=25, samples=None, verbose_name='Цвет фона')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
            },
        ),
        migrations.CreateModel(
            name='Topping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('name_ru', models.CharField(max_length=100, null=True, verbose_name='Название')),
                ('name_en', models.CharField(max_length=100, null=True, verbose_name='Название')),
                ('name_ky', models.CharField(max_length=100, null=True, verbose_name='Название')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='topping_photos/', verbose_name='Фото')),
            ],
            options={
                'verbose_name': 'Добавка',
                'verbose_name_plural': 'Добавки',
            },
        ),
        migrations.CreateModel(
            name='AttributeField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Название')),
                ('name_ru', models.CharField(blank=True, max_length=255, null=True, verbose_name='Название')),
                ('name_en', models.CharField(blank=True, max_length=255, null=True, verbose_name='Название')),
                ('name_ky', models.CharField(blank=True, max_length=255, null=True, verbose_name='Название')),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.attribute', verbose_name='Аттрибут')),
            ],
            options={
                'verbose_name': 'Поле Аттрибута',
                'verbose_name_plural': 'Поле Аттрибутов',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Название')),
                ('name_ru', models.CharField(max_length=50, null=True, verbose_name='Название')),
                ('name_en', models.CharField(max_length=50, null=True, verbose_name='Название')),
                ('name_ky', models.CharField(max_length=50, null=True, verbose_name='Название')),
                ('description', models.CharField(blank=True, max_length=100, verbose_name='Описание')),
                ('description_ru', models.CharField(blank=True, max_length=100, null=True, verbose_name='Описание')),
                ('description_en', models.CharField(blank=True, max_length=100, null=True, verbose_name='Описание')),
                ('description_ky', models.CharField(blank=True, max_length=100, null=True, verbose_name='Описание')),
                ('slug', models.SlugField(blank=True, max_length=100, null=True, unique=True, verbose_name='Ссылка')),
                ('image', models.FileField(blank=True, null=True, upload_to='category_photos/', verbose_name='Фото')),
                ('order', models.PositiveIntegerField(db_index=True, default=0, editable=False)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='product.category', verbose_name='Родительская категория')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('name_ru', models.CharField(max_length=255, null=True, verbose_name='Название')),
                ('name_en', models.CharField(max_length=255, null=True, verbose_name='Название')),
                ('name_ky', models.CharField(max_length=255, null=True, verbose_name='Название')),
                ('image', models.ImageField(max_length=1000, upload_to='form_photos/', verbose_name='Изображение')),
                ('attribute', models.ManyToManyField(to='product.attribute')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='forms', to='product.formcategory', verbose_name='Категория')),
                ('form_color', models.ManyToManyField(to='product.formcolor')),
                ('ornaments', models.ManyToManyField(to='product.ornament')),
            ],
            options={
                'verbose_name': 'Форма',
                'verbose_name_plural': 'Формы',
            },
        ),
        migrations.CreateModel(
            name='FormVariant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название команды')),
                ('logo', models.FileField(null=True, upload_to='logo', verbose_name='Логотип или Герб')),
                ('attribute_fields', models.ManyToManyField(to='product.attributefield', verbose_name='Аттрибуты')),
                ('color', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.formcolor', verbose_name='Цвет')),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.form', verbose_name='Форма')),
                ('ornament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.ornament', verbose_name='Орнамент')),
            ],
            options={
                'verbose_name': 'Вариант Формы',
                'verbose_name_plural': 'Варианты Формы',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_popular', models.BooleanField(default=False, verbose_name='Популярный')),
                ('is_new', models.BooleanField(default=False, verbose_name='Новинка')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('name_ru', models.CharField(max_length=100, null=True, verbose_name='Название')),
                ('name_en', models.CharField(max_length=100, null=True, verbose_name='Название')),
                ('name_ky', models.CharField(max_length=100, null=True, verbose_name='Название')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('description_ru', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('description_en', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('description_ky', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('photo', models.FileField(blank=True, null=True, upload_to='product_photos/', verbose_name='Фото')),
                ('bonuses', models.BooleanField(default=False, verbose_name='Можно оптатить бонусами')),
                ('order', models.PositiveIntegerField(db_index=True, default=0, editable=False)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('discounted_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Цена со скидкой')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='product.category', verbose_name='Категория')),
                ('country', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='product.country', verbose_name='Страна')),
                ('gender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='product.gender', verbose_name='Пол')),
                ('tags', models.ManyToManyField(blank=True, related_name='products', to='product.tag', verbose_name='Теги')),
            ],
            options={
                'verbose_name': 'Продукт',
                'verbose_name_plural': 'Продукты',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Characteristic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('name_ru', models.CharField(max_length=100, null=True, verbose_name='Название')),
                ('name_en', models.CharField(max_length=100, null=True, verbose_name='Название')),
                ('name_ky', models.CharField(max_length=100, null=True, verbose_name='Название')),
                ('value', models.CharField(max_length=255, verbose_name='Значение')),
                ('value_ru', models.CharField(max_length=255, null=True, verbose_name='Значение')),
                ('value_en', models.CharField(max_length=255, null=True, verbose_name='Значение')),
                ('value_ky', models.CharField(max_length=255, null=True, verbose_name='Значение')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_characteristics', to='product.product', verbose_name='Продукт')),
            ],
            options={
                'verbose_name': 'Характеристика',
                'verbose_name_plural': 'Характеристики',
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(upload_to='product_images/', verbose_name='Изображение')),
                ('color', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='color_images', to='product.color', verbose_name='Цвет')),
            ],
            options={
                'verbose_name': 'Изображение продукта',
                'verbose_name_plural': 'Изображения продуктов',
            },
        ),
        migrations.CreateModel(
            name='ProductSize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_colors', to='product.color', verbose_name='Цвета')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_sizes', to='product.product', verbose_name='Продукт')),
                ('sizes', models.ManyToManyField(related_name='product_sizes', to='product.size', verbose_name='Размеры')),
            ],
            options={
                'verbose_name': 'Цена продукта по размеру',
                'verbose_name_plural': 'Цены продуктов по размерам',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveIntegerField(default=5, verbose_name='Рейтинг')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Комментарий')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_reviews', to='product.product', verbose_name='Продукт')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_reviews', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Отзыв',
                'verbose_name_plural': 'Отзывы',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Set',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='topping_photos/', verbose_name='Фото')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('bonus_price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Цена бонусами')),
                ('bonuses', models.BooleanField(default=False, verbose_name='Можно оптатить бонусами')),
                ('discounted_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Цена со скидкой')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sets', to='product.category', verbose_name='Категория')),
                ('products', models.ManyToManyField(related_name='sets', to='product.productsize', verbose_name='Продукты')),
            ],
            options={
                'verbose_name': 'Сет',
                'verbose_name_plural': 'Сеты',
            },
        ),
        migrations.CreateModel(
            name='FavoriteProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_products', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='product.product', verbose_name='Продукт')),
            ],
            options={
                'verbose_name': 'Избранный продукт',
                'verbose_name_plural': 'Избранные продукты',
                'unique_together': {('user', 'product')},
            },
        ),
    ]
