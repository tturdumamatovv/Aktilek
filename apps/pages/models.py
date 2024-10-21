from colorfield.fields import ColorField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from ckeditor.fields import RichTextField
from unidecode import unidecode

from apps.authentication.models import User
from apps.product.models import Product, Category


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super(SingletonModel, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        if not cls.objects.exists():
            cls.objects.create()
        return cls.objects.get()


class MainPage(SingletonModel):
    icon = models.FileField(
        upload_to="images/icons",
        verbose_name=_("Логотип"),
        help_text=_("Логотип для главной страницы.")
    )
    phone = models.CharField(
        max_length=20,
        verbose_name=_("Телефон"),
        help_text=_("Контактный телефон для главной страницы.")
    )
    meta_title = models.CharField(
        max_length=255,
        verbose_name=_("Мета заголовок"),
        blank=True,
        null=True
    )
    meta_description = models.CharField(
        max_length=255,
        verbose_name=_("Мета описание"),
        blank=True,
        null=True
    )
    meta_image = models.ImageField(
        upload_to="images/meta",
        verbose_name=_("Мета изображение"),
        blank=True,
        null=True
    )
    meta_keywords = models.TextField(verbose_name=_('Ключевые слова (keywords)'), help_text=_('Ключевые слова для SEO'),
                                     blank=True, null=True)
    maintenance = models.BooleanField(default=False, verbose_name=_("Технические работы"))

    class Meta:
        verbose_name = _("Главная страница")
        verbose_name_plural = _("Главная страница")

    def __str__(self):
        return self.phone


class OrderTypes(models.Model):
    page = models.ForeignKey(MainPage, on_delete=models.CASCADE, related_name='order_types')
    image = models.ImageField(verbose_name=_("Изображение"), blank=True, null=True)
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"))
    description = models.TextField(verbose_name=_("Описание"))

    class Meta:
        verbose_name = _("Тип заказа")
        verbose_name_plural = _("Типы заказа")


class DeliveryConditions(models.Model):
    page = models.ForeignKey(MainPage, related_name='delivery_conditions', on_delete=models.CASCADE)
    image = models.ImageField(verbose_name=_("Изображение"), blank=True, null=True)
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"))
    description = models.TextField(verbose_name=_("Описание"))

    class Meta:
        verbose_name = _("Условия доставки")
        verbose_name_plural = _("Условия доставки")


class MethodsOfPayment(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"))
    description = RichTextField(verbose_name=_("Описание"))
    online_payment = models.BooleanField(default=True, verbose_name=_("Оплата онлайн"))

    class Meta:
        verbose_name = _("Способ оплаты")
        verbose_name_plural = _("Способы оплаты")

    def __str__(self):
        return self.title


class Redirection(models.Model):
    page = models.ForeignKey(MainPage, related_name='redirection', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"))
    description = RichTextField(verbose_name=_("Описание"))
    link = models.URLField(verbose_name=_("Ссылка"))
    link_2 = models.URLField(verbose_name=_("Дополнительная ссылка"))
    image = models.FileField(upload_to='pages/redirection/', verbose_name=_("Изображение"))

    class Meta:
        verbose_name = _("Способ оплаты")
        verbose_name_plural = _("Способы оплаты")

    def __str__(self):
        return self.title


class StaticPage(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"))
    description = RichTextField(verbose_name=_("Описание"))
    slug = models.SlugField(unique=True, verbose_name=_("Слаг"), blank=True, null=True)
    image = models.FileField(verbose_name=_("Изображение"), upload_to="images/static", blank=True, null=True, max_length=5000)
    meta_title = models.CharField(max_length=255, verbose_name=_("Мета заголовок"), blank=True, null=True)
    meta_description = models.CharField(max_length=255, verbose_name=_("Мета описание"), blank=True, null=True)
    meta_image = models.FileField(verbose_name=_("Мета изображение"), upload_to="images/meta", blank=True, null=True)

    class Meta:
        verbose_name = _("Статическая страница")
        verbose_name_plural = _("Статические страницы")

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(unidecode(self.title))
            slug = base_slug
            counter = 1

            # Проверяем, существует ли уже такой slug
            while StaticPage.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


class Banner(models.Model):
    TYPE_CHOICES = (
        ('category', 'Категория'),
        ('product', 'Продукт'),
        ('link', 'Отдельная ссылка'),
    )
    type = models.CharField(verbose_name="Тип баннера", max_length=10, choices=TYPE_CHOICES, default='product')
    product = models.ForeignKey(Product, verbose_name="Продукт", on_delete=models.CASCADE, blank=True, null=True)
    category = models.ForeignKey(Category, verbose_name="Категория", on_delete=models.CASCADE, blank=True, null=True)
    link = models.URLField(verbose_name="Ссылка", max_length=200, blank=True, null=True)
    title = models.CharField(verbose_name="Заголовок", max_length=123, blank=True, null=True)
    image_desktop = models.ImageField(verbose_name="Картинка круп", upload_to="images/banners/desktop/%Y/%m/", max_length=5000)
    image_mobile = models.ImageField(verbose_name="Картинка моб", upload_to="images/banners/mobile/%Y/%m/", max_length=5000)
    is_active = models.BooleanField(verbose_name="Активный", default=True)
    is_top = models.BooleanField(verbose_name="Верхний баннер", default=False)  # Новое поле
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True, blank=True, null=True)

    class Meta:
        verbose_name = "Баннер"
        verbose_name_plural = "Баннеры"
        ordering = ["is_active", "-created_at"]

    def get_image_desktop(self):
        if self.image_desktop:
            return mark_safe(
                f'<img src="{self.image_desktop.url}" width="328" height="100" />'
            )
        return ""

    def get_image_mobile(self):
        if self.image_mobile:
            return mark_safe(
                f'<img src="{self.image_mobile.url}" width="328" height="100" />'
            )
        return ""

    def __str__(self):
        return f"{self.title}"

    def clean(self):
        if self.type == 'category':
            if not self.category:
                raise ValidationError("Для типа 'Категория' необходимо указать категорию.")
            self.product = None
            self.link = ''
        elif self.type == 'product':
            if not self.product:
                raise ValidationError("Для типа 'Продукт' необходимо указать продукт.")
            self.category = None
            self.link = ''
        elif self.type == 'link':
            if not self.link:
                raise ValidationError("Для типа 'Отдельная ссылка' необходимо указать ссылку.")
            self.product = None
            self.category = None
        super().clean()


class Contacts(SingletonModel):
    pass

    def __str__(self):
        return 'Контактная информация'

    class Meta:
        verbose_name = 'Контакты'
        verbose_name_plural = 'Контакты'


class Phone(models.Model):
    contacts = models.ForeignKey(Contacts, on_delete=models.CASCADE)
    phone = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.phone}'

    class Meta:
        verbose_name = 'Телефон'
        verbose_name_plural = 'Телефоны'


class Email(models.Model):
    contacts = models.ForeignKey(Contacts, on_delete=models.CASCADE)
    email = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.email}'

    class Meta:
        verbose_name = 'Имейл'
        verbose_name_plural = 'Имейлы'


class SocialLink(models.Model):
    contacts = models.ForeignKey(Contacts, on_delete=models.CASCADE)
    link = models.CharField(max_length=100)
    icon = models.FileField(upload_to='social_icons')

    def __str__(self):
        return f'{self.link}'

    class Meta:
        verbose_name = 'Ссылка соцсети'
        verbose_name_plural = 'Ссылки соцсетей'


class Address(models.Model):
    contacts = models.ForeignKey(Contacts, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'


class PaymentMethod(models.Model):
    contacts = models.ForeignKey(Contacts, on_delete=models.CASCADE)
    link = models.CharField(max_length=100)
    icon = models.FileField(upload_to='payment_icons')

    def __str__(self):
        return f'{self.link}'

    class Meta:
        verbose_name = 'Ссылка для оплаты'
        verbose_name_plural = 'Ссылки для оплаты'


class Stories(models.Model):
    title = models.CharField(verbose_name="Заголовок", max_length=123, blank=True, null=True)
    image = models.ImageField(verbose_name="Изображение", upload_to="images/stories", blank=True, null=True)
    is_active = models.BooleanField(verbose_name="Активный", default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Группа историй"
        verbose_name_plural = "Группы историй"


class Story(models.Model):
    stories = models.ForeignKey(Stories, on_delete=models.CASCADE, related_name='stories')
    image = models.ImageField(verbose_name="Изображение", upload_to="images/stories", blank=True, null=True)
    TYPE_CHOICES = (
        ('category', 'Категория'),
        ('product', 'Продукт'),
        ('link', 'Отдельная ссылка'),
    )
    type = models.CharField(verbose_name="Тип баннера", max_length=10, choices=TYPE_CHOICES, default='product')
    product = models.ForeignKey(Product, verbose_name="Продукт", on_delete=models.CASCADE, blank=True, null=True)
    category = models.ForeignKey(Category, verbose_name="Категория", on_delete=models.CASCADE, blank=True, null=True)
    link = models.URLField(verbose_name="ссылка", max_length=200, blank=True, null=True)

    is_active = models.BooleanField(verbose_name="Активный", default=True)
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True, blank=True, null=True)

    def clean(self):
        if self.type == 'category':
            if not self.category:
                raise ValidationError("Для типа 'Категория' необходимо указать категорию.")
            self.product = None
            self.link = ''
        elif self.type == 'product':
            if not self.product:
                raise ValidationError("Для типа 'Продукт' необходимо указать продукт.")
            self.category = None
            self.link = ''
        elif self.type == 'link':
            if not self.link:
                raise ValidationError("Для типа 'Отдельная ссылка' необходимо указать ссылку.")
            self.product = None
            self.category = None
        super().clean()

    def __str__(self):
        return f'{self.id}'

    class Meta:
        verbose_name = "История"
        verbose_name_plural = "Истории"


class StoriesUserCheck(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories_user_check')
    stories = models.ForeignKey(Stories, on_delete=models.CASCADE, related_name='stories_user_check')
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True, blank=True, null=True)


class SiteSettings(SingletonModel):
    site_name = models.CharField(max_length=255, verbose_name="Название сайта")
    site_description = models.TextField(verbose_name="Описание сайта")
    site_logo = models.FileField(upload_to="site_logos", verbose_name="Логотип сайта", blank=True, null=True)
    site_bottom_logo = models.FileField(upload_to="site_logos", verbose_name="Логотип нижней части сайта", blank=True,
                                        null=True)
    site_favicon = models.FileField(upload_to="site_favicons", verbose_name="Иконка сайта", blank=True, null=True)

    def __str__(self):
        return self.site_name

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"


class BonusPage(SingletonModel):
    mobile_app_image = models.FileField(upload_to="bonus_pages", verbose_name="Мобильное приложение", blank=True,
                                        null=True)
    mobile_app_text = models.TextField(verbose_name="Текст приложения", blank=True, null=True)
    mobile_app_color = ColorField(default='#000000', verbose_name="Цвет карточки приложения", blank=True, null=True)
    bonus_image = models.FileField(upload_to="bonus_pages", verbose_name="Картинка карточки бонусов", blank=True,
                                   null=True)
    bonus_title = models.CharField(max_length=255, verbose_name="Заголовок карточки бонусов", blank=True, null=True)
    bonus_text = models.TextField(verbose_name="Текст карточки бонусов", blank=True, null=True)
    bonus_color = ColorField(default='#000000', verbose_name="Цвет карточки бонусов", blank=True, null=True)
    bottom_card_text = models.TextField(verbose_name="Нижняя часть карточки", blank=True, null=True)
    bottom_cart_color = ColorField(default='#000000', verbose_name="Цвет нижней части карточки", blank=True, null=True)

    def __str__(self):
        return "Бонусная страница"

    class Meta:
        verbose_name = "Бонусная страница"
        verbose_name_plural = "Бонусная страница"


class Advertisement(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    image = models.ImageField(upload_to='advertisements/', blank=True, null=True, verbose_name="Изображение")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Реклама"
        verbose_name_plural = "Рекламные объявления"


class News(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    description = RichTextField(verbose_name="Описание")  # CKEditor для текстового редактора
    image = models.ImageField(upload_to='images/news', verbose_name="Изображение", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
