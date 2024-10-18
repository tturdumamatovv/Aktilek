from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline, StackedInline

from apps.pages.models import (
    Banner,
    Phone,
    StaticPage,
    Email,
    SocialLink,
    PaymentMethod,
    Address,
    Contacts,
    MethodsOfPayment,
    DeliveryConditions,
    OrderTypes,
    MainPage,
    Stories,
    Story,
    SiteSettings,
    BonusPage,
    Advertisement,
    News,
    Redirection
)
from apps.services.firebase_notification import send_firebase_notification


@admin.register(Banner)
class BannerAdmin(ModelAdmin):
    list_display = ["title", "type", 'object_link', "is_active", "created_at"]
    list_filter = ["title", "is_active", "created_at"]
    search_fields = ["title", "link", "created_at"]
    date_hierarchy = "created_at"
    fields = (
        "type",
        "product",
        "category",
        "link",
        "title",
        "image_desktop",
        "get_image_desktop",
        "image_mobile",
        "get_image_mobile",
        "is_active",
        "is_top",
        "created_at",
    )
    readonly_fields = ("get_image_desktop", "get_image_mobile", "created_at")

    def object_link(self, obj):
        if obj.type == 'category' and obj.category:
            # Ссылка на категорию, предполагается что у категории есть метод get_absolute_url()
            return format_html('<a href="{}">{}</a>', obj.category.get_absolute_url(), obj.category)
        elif obj.type == 'product' and obj.product:
            # Ссылка на продукт, предполагается что у продукта есть метод get_absolute_url()
            return format_html('<a href="{}">{}</a>', obj.product.get_absolute_url(), obj.product)
        elif obj.type == 'link' and obj.link:
            # Прямая внешняя ссылка
            return format_html('<a href="{}">{}</a>', obj.link, obj.link)
        return None  # Возвращаем None, если условия не выполняются

    object_link.short_description = "Ссылка объекта"


@admin.register(StaticPage)
class StaticPageAdmin(ModelAdmin):
    exclude = [
        'title',
        'description',
    ]


class PhoneInline(TabularInline):
    model = Phone
    extra = 0


class EmailInline(TabularInline):
    model = Email
    extra = 0


class SocialLinkInline(TabularInline):
    model = SocialLink
    extra = 0


class PaymentMethodLinkInline(TabularInline):
    model = PaymentMethod
    extra = 0


class AddressInline(TabularInline):
    model = Address
    extra = 0


@admin.register(Contacts)
class ContactsAdmin(ModelAdmin):
    pass
    inlines = [PhoneInline, EmailInline, SocialLinkInline, PaymentMethodLinkInline, AddressInline]


class OrderTypesInline(TabularInline):
    model = OrderTypes
    extra = 0


class DeliveryConditionsInline(TabularInline):
    model = DeliveryConditions
    extra = 0


@admin.register(MethodsOfPayment)
class MethodsOfPaymentAdmin(ModelAdmin):
    list_display = ('title', 'description', 'online_payment')


class RedirectionInline(StackedInline):
    model = Redirection
    extra = 0
    exclude = ('title', 'description')


@admin.register(MainPage)
class MainPageAdmin(ModelAdmin):
    list_display = ('phone', 'icon', 'meta_title', 'meta_description', 'meta_image')
    inlines = [RedirectionInline]


class StoryInline(TabularInline):
    extra = 0
    model = Story


@admin.register(Stories)
class StoriesAdmin(ModelAdmin):
    inlines = [StoryInline]


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    pass


@admin.register(BonusPage)
class BonusPageAdmin(ModelAdmin):
    pass


@admin.register(Advertisement)
class AdvertisementAdmin(ModelAdmin):
    list_display = ('title', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'content')
    actions = ['send_advertisement']

    def send_advertisement(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Пожалуйста, выберите только одно рекламное объявление", level=messages.WARNING)
            return

        ad = queryset.first()
        users = User.objects.filter(receive_notifications=True)

        success_count = 0
        for user in users:
            if user.fcm_token:
                try:
                    # Полный URL для изображения
                    image_url = request.build_absolute_uri(ad.image.url) if ad.image else None
                    print({
                            'type': 'advertisement',
                            'ad_id': str(ad.id),
                            'image_url': image_url
                        })

                    send_firebase_notification(
                        token=user.fcm_token,
                        title=ad.title,
                        body=ad.content,
                        data={
                            'type': 'advertisement',
                            'ad_id': str(ad.id),
                            'image_url': image_url
                        }
                    )
                    success_count += 1
                except Exception as e:
                    self.message_user(request, f"Ошибка при отправке уведомления пользователю {user.id}: {str(e)}",
                                      level=messages.ERROR)
            else:
                self.message_user(request, f"У пользователя {user.id} отсутствует токен Firebase",
                                  level=messages.WARNING)

        self.message_user(request, f"Реклама успешно отправлена {success_count} из {users.count()} пользователей",
                          level=messages.SUCCESS)

    send_advertisement.short_description = "Отправить выбранную рекламу всем пользователям"


@admin.register(News)
class NewsAdmin(ModelAdmin):
    list_display = ['title', 'created_at']
    search_fields = ['title', 'description']
    list_filter = ['created_at']
    date_hierarchy = 'created_at'
    fields = ('title', 'image', 'description')
