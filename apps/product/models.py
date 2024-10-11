import os
from io import BytesIO

from mptt.models import MPTTModel, TreeForeignKey

from PIL import Image
from colorfield.fields import ColorField
from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from unidecode import unidecode

from apps.authentication.models import User


class Size(models.Model):
    name = models.CharField(max_length=50, verbose_name=_('Название'))
    description = models.CharField(max_length=100, blank=True, verbose_name=_('Описание'))

    class Meta:
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Название'))
    text_color = ColorField(default='#FF0000', format='hex', verbose_name=_('Цвет текста'))
    background_color = ColorField(default='#FF0000', format='hex', verbose_name=_('Цвет фона'))

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Category(MPTTModel):
    name = models.CharField(max_length=50, verbose_name=_('Название'))
    description = models.CharField(max_length=100, blank=True, verbose_name=_('Описание'))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_('Ссылка'), blank=True, null=True)
    image = models.FileField(upload_to='category_photos/', verbose_name=_('Фото'), blank=True, null=True)
    order = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, related_name='subcategories',
                               verbose_name=_('Родительская категория'), blank=True, null=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['order']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/admin/product/category/{self.id}/change/"

    def has_subcategories(self):
        """Проверяет, есть ли у категории подкатегории."""
        return self.subcategories.exists()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)


class Product(models.Model):
    GENDER_CHOICES = (
        ('M', 'Мужчинам'),
        ('F', 'Женщинам'),
        ('C', 'Детям'),
        ('A', 'Животным'),
    )
    is_popular = models.BooleanField(default=False, verbose_name=_('Популярный'))
    is_new = models.BooleanField(default=False, verbose_name=_('Новинка'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('Категория'),
                                 related_name='products', blank=True, null=True)
    name = models.CharField(max_length=100, verbose_name=_('Название'))
    description = models.TextField(verbose_name=_('Описание'), blank=True, null=True)
    photo = models.FileField(upload_to='product_photos/', verbose_name=_('Фото'), blank=True, null=True)
    toppings = models.ManyToManyField('Topping', related_name='products', verbose_name=_('Добавки'), blank=True)
    bonuses = models.BooleanField(default=False, verbose_name=_('Можно оптатить бонусами'))
    tags = models.ManyToManyField('Tag', related_name='products', verbose_name=_('Теги'), blank=True)
    order = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    country = models.CharField(max_length=255, verbose_name=_("Страна"), blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name=_('Пол'), blank=True, null=True)

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ['order']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/admin/product/product/{self.id}/change/"

    def get_min_price(self):
        prices = [size.discounted_price if size.discounted_price else size.price for size in self.product_sizes.all()]
        return min(prices) if prices else None

    def process_and_save_image(self):
        """ Обрабатывает и сохраняет изображение, преобразуя его в формат .webp и изменяя размер, и удаляет старое изображение если нужно """
        if not self.photo:
            return

        # Путь к текущему файлу перед изменением
        old_path = self.photo.path if self.photo.name else None

        # Проверяем, нужно ли преобразование
        if not self.photo.name.endswith('.webp'):
            image = Image.open(self.photo)

            max_width = 800
            max_height = 800

            original_width, original_height = image.size
            ratio = min(max_width / original_width, max_height / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)

            resized_image = image.resize((new_width, new_height), Image.LANCZOS)

            image_io = BytesIO()
            resized_image.save(image_io, format='WEBP', quality=85)

            new_name = f"{self.photo.name.rsplit('.', 1)[0]}.webp"
            self.photo.save(new_name, ContentFile(image_io.getvalue()), save=False)

        # Вызов родительского метода save
        super().save()

        # Удаление старого файла, если путь существует и файл был обновлён
        if old_path and old_path != self.photo.path:
            if os.path.isfile(old_path):
                os.remove(old_path)

    def save(self, *args, **kwargs):
        if self.category and self.category.has_subcategories():
            raise ValidationError(
                _('Нельзя создавать продукт в категории, которая имеет подкатегории. Выберите конечную категорию.'))

        self.process_and_save_image()
        super().save(*args, **kwargs)


class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_sizes',
                                verbose_name=_('Продукт'))
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name='product_sizes', verbose_name=_('Размер'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Цена'))
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Цена со скидкой'),
                                           blank=True, null=True)
    bonus_price = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name=_('Цена бонусами'))
    colors = models.ManyToManyField('Color', related_name='product_sizes', verbose_name=_('Цвета'))

    class Meta:
        verbose_name = "Цена продукта по размеру"
        verbose_name_plural = "Цены продуктов по размерам"

    def get_price(self):
        return self.discounted_price if self.discounted_price else self.price

    def get_images_for_color(self, color):
        """Получает изображения для данного размера продукта по указанному цвету."""
        return self.images.filter(color=color)

    def __str__(self):
        return f"{self.product.name} - {self.size.name} - {self.get_price()}"


class Topping(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Название'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Цена'))
    photo = models.ImageField(upload_to='topping_photos/', verbose_name=_('Фото'), blank=True, null=True)

    class Meta:
        verbose_name = "Добавка"
        verbose_name_plural = "Добавки"

    def __str__(self):
        return self.name


class Set(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('Категория'), related_name='sets')
    name = models.CharField(max_length=100, verbose_name=_('Название'))
    description = models.TextField(verbose_name=_('Описание'), blank=True, null=True)
    photo = models.ImageField(upload_to='topping_photos/', verbose_name=_('Фото'), blank=True, null=True)
    products = models.ManyToManyField(ProductSize, related_name='sets', verbose_name=_('Продукты'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Цена'))
    bonus_price = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name=_('Цена бонусами'))
    bonuses = models.BooleanField(default=False, verbose_name=_('Можно оптатить бонусами'))
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Цена со скидкой'),
                                           blank=True, null=True)

    class Meta:
        verbose_name = "Сет"
        verbose_name_plural = "Сеты"

    def __str__(self):
        return self.name

    def get_price(self):
        return self.discounted_price if self.discounted_price else self.price


class Ingredient(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Название'))
    photo = models.ImageField(upload_to='topping_photos/', verbose_name=_('Фото'), blank=True, null=True)
    possibly_remove = models.BooleanField(default=False, verbose_name=_('Возможность удаления'))

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class FavoriteProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_products', verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by', verbose_name='Продукт')

    class Meta:
        verbose_name = "Избранный продукт"
        verbose_name_plural = "Избранные продукты"
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user} - {self.product}"


class Color(models.Model):
    name = models.CharField(max_length=50, verbose_name=_('Цвет'))
    hex_code = ColorField(default='#FFFFFF', format='hex', verbose_name=_('HEX Код'))

    class Meta:
        verbose_name = "Цвет"
        verbose_name_plural = "Цвета"

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product_size = models.ForeignKey(ProductSize, on_delete=models.CASCADE, related_name='images', verbose_name=_('Размер продукта'))
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='color_images', verbose_name=_('Цвет'))
    image = models.FileField(upload_to='product_images/', verbose_name=_('Изображение'))

    class Meta:
        verbose_name = "Изображение продукта"
        verbose_name_plural = "Изображения продуктов"

    def __str__(self):
        return f"{self.product_size.product.name} - {self.color.name}"

    def process_and_save_image(self):
        """Обрабатывает и сохраняет изображение, преобразуя его в формат .webp и изменяя размер."""
        if not self.image:
            return

        # Путь к текущему файлу перед изменением
        old_path = self.image.path if self.image.name else None

        # Проверяем, нужно ли преобразование
        if not self.image.name.endswith('.webp'):
            image = Image.open(self.image)

            max_width = 800
            max_height = 800

            original_width, original_height = image.size
            ratio = min(max_width / original_width, max_height / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)

            resized_image = image.resize((new_width, new_height), Image.LANCZOS)

            # Сохранение изображения в памяти
            image_io = BytesIO()
            resized_image.save(image_io, format='WEBP', quality=85)

            new_name = f"{self.image.name.rsplit('.', 1)[0]}.webp"
            self.image.save(new_name, ContentFile(image_io.getvalue()), save=False)

        # Вызов родительского метода save
        super().save()

        # Удаление старого файла, если путь существует и файл был обновлён
        if old_path and old_path != self.image.path:
            if os.path.isfile(old_path):
                os.remove(old_path)

    def save(self, *args, **kwargs):
        self.process_and_save_image()
        super().save(*args, **kwargs)


class Characteristic(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Название'))
    value = models.CharField(max_length=255, verbose_name=_('Значение'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_characteristics', verbose_name=_('Продукт'))

    class Meta:
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"

    def __str__(self):
        return f"{self.name}: {self.value}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_reviews', verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_reviews', verbose_name='Продукт')
    rating = models.PositiveIntegerField(default=5, verbose_name=_('Рейтинг'))
    comment = models.TextField(verbose_name=_('Комментарий'), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.phone_number} - {self.product.name} - {self.rating}/5"


class FormCategory(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Название'))
    description = models.CharField(max_length=255, blank=True, verbose_name=_('Описание'))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_('Ссылка'), blank=True, null=True)

    class Meta:
        verbose_name = "Категория формы"
        verbose_name_plural = "Категории форм"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)


class Form(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Название'))
    image = models.ImageField(upload_to='form_photos/', verbose_name=_('Изображение'), max_length=1000)
    category = models.ForeignKey(FormCategory, related_name='forms', on_delete=models.CASCADE, verbose_name=_('Категория'))
    ornaments = models.ManyToManyField('Ornament')
    form_color = models.ManyToManyField('FormColor')
    attribute = models.ManyToManyField('Attribute')

    class Meta:
        verbose_name = _("Форма")
        verbose_name_plural = _("Формы")

    def __str__(self):
        return self.name

    def process_and_save_image(self):
        """ Обрабатывает и сохраняет изображение, преобразуя его в формат .webp и изменяя размер, и удаляет старое изображение если нужно """
        if not self.image:
            return

        # Путь к текущему файлу перед изменением
        old_path = self.image.path if self.image.name else None

        # Проверяем, нужно ли преобразование
        if not self.image.name.endswith('.webp'):
            image = Image.open(self.image)

            max_width = 800
            max_height = 800

            original_width, original_height = image.size
            ratio = min(max_width / original_width, max_height / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)

            resized_image = image.resize((new_width, new_height), Image.LANCZOS)

            image_io = BytesIO()
            resized_image.save(image_io, format='WEBP', quality=85)

            new_name = f"{self.image.name.rsplit('.', 1)[0]}.webp"
            self.image.save(new_name, ContentFile(image_io.getvalue()), save=False)

        # Вызов родительского метода save
        super().save()

        # Удаление старого файла, если путь существует и файл был обновлён
        if old_path and old_path != self.image.path:
            if os.path.isfile(old_path):
                os.remove(old_path)

    def save(self, *args, **kwargs):
        self.process_and_save_image()
        super().save(*args, **kwargs)


class Ornament(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Название"), null=True, blank=True)
    image = models.FileField(max_length=500, verbose_name=_("Орнамент"), upload_to='ornament', null=True, blank=True)

    class Meta:
        verbose_name = _("Орнамент")
        verbose_name_plural = _("Орнаменты")

    def __str__(self):
        return self.name


class FormColor(models.Model):
    name = models.CharField(max_length=50, verbose_name=_('Цвет'))
    hex_code = ColorField(default='#FFFFFF', format='hex', verbose_name=_('HEX Код'))

    class Meta:
        verbose_name = "Цвет Формы"
        verbose_name_plural = "Цвета для Форм"

    def __str__(self):
        return self.name


class Attribute(models.Model):
    type = models.CharField(max_length=255, verbose_name=_("Тип"), null=True, blank=True)

    class Meta:
        verbose_name = _("Аттрибут")
        verbose_name_plural = _("Аттрибуты")

    def __str__(self):
        return self.type


class AttributeField(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Название"), null=True, blank=True)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, verbose_name=_('Аттрибут'))

    class Meta:
        verbose_name = _("Поле Аттрибута")
        verbose_name_plural = _("Поле Аттрибутов")

    def __str__(self):
        return f'{self.attribute} - {self.name}'


class FormVariant(models.Model):
    color = models.ForeignKey(FormColor, on_delete=models.CASCADE, verbose_name=_('Цвет'))
    ornament = models.ForeignKey(Ornament, on_delete=models.CASCADE, verbose_name=_('Орнамент'))
    name = models.CharField(max_length=255, verbose_name=_("Название команды"))
    logo = models.FileField(upload_to='logo', verbose_name=_("Логотип или Герб"), null=True)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, verbose_name=_('Форма'))
    attribute_fields = models.ManyToManyField(AttributeField, verbose_name=_("Аттрибуты"))

    class Meta:
        verbose_name = _("Вариант Формы")
        verbose_name_plural = _("Варианты Формы")

    def __str__(self):
        return self.name


class OrderRequest(models.Model):
    full_name = models.CharField(max_length=255, verbose_name=_('Имя Фамилия'))
    email = models.EmailField(verbose_name=_('Электронная почта'))
    phone_number = models.CharField(max_length=20, verbose_name=_('Номер для связи'))
    city_region = models.CharField(max_length=255, verbose_name=_('Город/регион'))
    quantity = models.IntegerField(verbose_name=_('Предполагаемое количество единиц'))
    delivery_date = models.DateField(verbose_name=_('Когда требуется заказ?'))
    comments = models.TextField(blank=True, null=True, verbose_name=_('Ваш комментарий'))

    class Meta:
        verbose_name = _('Заявка')
        verbose_name_plural = _('Заявки')

    def __str__(self):
        return f"{self.full_name} - {self.city_region}"
