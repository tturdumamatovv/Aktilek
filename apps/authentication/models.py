from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None):
        if not phone_number:
            raise ValueError('Необходимо указать номер телефона')

        user = self.model(phone_number=phone_number)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None):
        user = self.create_user(phone_number, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=13, unique=True, verbose_name=_('Номер телефона'))
    code = models.CharField(max_length=4, blank=True, null=True, verbose_name=_('Код'))
    is_staff = models.BooleanField(default=False, verbose_name=_('Работник'))
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, max_length=255,
                                        verbose_name=_('Изображение профиля'))
    full_name = models.CharField(max_length=255, blank=True, verbose_name=_('Полное имя'))
    date_of_birth = models.DateField(blank=True, null=True, verbose_name=_('Дата рождения'))
    email = models.EmailField(blank=True, verbose_name=_('Имейл'))
    first_visit = models.BooleanField(default=True, verbose_name=_('Дата первого визита'))
    fcm_token = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Токен'))
    receive_notifications = models.BooleanField(default=False, verbose_name=_('Получать уведомления'), null=True,
                                                blank=True)
    last_order = models.DateTimeField(null=True, blank=True, verbose_name=_("Последний заказ"))
    bonus = models.DecimalField(max_digits=9, decimal_places=2, verbose_name=_('Бонусы'), null=True, blank=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def get_admin_url(self):
        return f"/admin/authentication/user/{self.id}/change/"

    def __str__(self):
        return self.phone_number

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _("Пользователи")


class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name=_("Пользователь"))
    city = models.CharField(max_length=100, verbose_name=_("Адрес"), null=True, blank=True)
    # street = models.CharField(max_length=100, verbose_name=_("Улица"), null=True, blank=True)
    # house_number = models.CharField(max_length=10, verbose_name=_("Номер дома"), null=True, blank=True)
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
        verbose_name = _("Адрес пользователя")
        verbose_name_plural = _("Адреса пользователей")
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.city}'  # - {self.street} {self.house_number}'
