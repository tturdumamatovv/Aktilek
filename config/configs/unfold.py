from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from django.utils.functional import cached_property


class Config:
    @cached_property
    def main_page(self):
        from apps.pages.models import MainPage  # Отложенный импорт
        return MainPage.objects.first()


UNFOLD = {
    "SITE_TITLE": "Aktilek Admin",
    "SITE_HEADER": "Aktilek Admin",
    "SITE_URL": "/",
    "SITE_ICON": lambda request: static(Config().main_page.icon.url) if Config().main_page and Config().main_page.icon else None,  # both modes, optimise for 32px height
    # "SITE_ICON": {
    #     "light": lambda request: static("icon-light.svg"),  # light mode
    #     "dark": lambda request: static("icon-dark.svg"),  # dark mode
    # },
    "SITE_LOGO": lambda request: static(Config().main_page.icon.url) if Config().main_page and Config().main_page.icon else None,  # both modes, optimise for 32px height
    # "SITE_LOGO": {
    #     "light": lambda request: static("logo-light.svg"),  # light mode
    #     "dark": lambda request: static("logo-dark.svg"),  # dark mode
    # },
    "SITE_SYMBOL": "speed",  # symbol from icon set
    # "SITE_FAVICONS": [
    #     {
    #         "rel": "icon",
    #         "sizes": "32x32",
    #         "type": "image/svg+xml",
    #         "href": lambda request: static("favicon.svg"),
    #     },
    # ],
    "SHOW_HISTORY": False,  # show/hide "History" button, default: True
    "SHOW_VIEW_ON_SITE": True,  # show/hide "View on site" button, default: True
    # "ENVIRONMENT": "sample_app.environment_callback",
    # "DASHBOARD_CALLBACK": "sample_app.dashboard_callback",
    "LOGIN": {
        # "image": lambda request: static("sample/login-bg.jpg"),
        "redirect_after": lambda request: reverse_lazy("admin:authentication_user_changelist"),
    },
    # "STYLES": [
    #     lambda request: static("css/style.css"),
    # ],
    # "SCRIPTS": [
    #     lambda request: static("js/script.js"),
    # ],
    "COLORS": {
        "font": {
            "subtle-light": "107 114 128",
            "subtle-dark": "156 163 175",
            "default-light": "75 85 99",
            "default-dark": "209 213 219",
            "important-light": "17 24 39",
            "important-dark": "243 244 246",
        },
        "primary": {
            "50": "255 244 230",
            "100": "255 230 204",
            "200": "255 215 179",
            "300": "255 196 143",
            "400": "255 171 87",
            "500": "255 145 0",
            "600": "234 128 0",
            "700": "202 111 0",
            "800": "171 92 0",
            "900": "140 74 0",
            "950": "112 59 0"
        }
    },
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "ru": "🇷🇺",
                "ky": "🇰🇬",
                "kk": "🇰🇿",
            },
        },
    },
    "SIDEBAR": {
        "show_search": True,  # Отключить поиск в именах приложений и моделей
        "show_all_applications": True,  # Отключить раскрывающееся меню со всеми приложениями и моделями
        "navigation": [
            {
                "title": _("Пользователи"),
                "icon": "person",
                "collapsible": True,
                "items": [
                    {
                        "title": _("Адреса пользователей"),
                        "icon": "home",
                        "link": reverse_lazy("admin:authentication_useraddress_changelist"),
                    },
                    {
                        "title": _("Пользователи"),
                        "icon": "person",
                        "link": reverse_lazy("admin:authentication_user_changelist"),
                    },
                    {
                        "title": _("Чаты"),
                        "icon": "chat",
                        "link": reverse_lazy("admin:chat_chat_changelist"),
                    },
                ],
            },
            {
                "title": _("Заказы"),
                "icon": "restaurant",
                "collapsible": True,
                "items": [
                    {
                        "title": _("Склады"),
                        "icon": "archive",
                        "link": reverse_lazy("admin:orders_warehouse_changelist"),
                    },
                    {
                        "title": _("Заказы"),
                        "icon": "archive",
                        "link": reverse_lazy("admin:orders_order_changelist"),
                    },
                ],
            },
            {
                "title": _("Продукты"),
                "icon": "fastfood",
                "collapsible": True,
                "items": [
                    {
                        "title": _("Продукты"),
                        "icon": "laundry",
                        "link": reverse_lazy("admin:product_product_changelist"),
                    },
                    {
                        "title": _("Категории"),
                        "icon": "category",
                        "link": reverse_lazy("admin:product_category_changelist"),
                    },
                    {
                        "title": _("Размеры"),
                        "icon": "straighten",
                        "link": reverse_lazy("admin:product_size_changelist"),
                    },
                    {
                        "title": _("Цвета"),
                        "icon": "colors",
                        "link": reverse_lazy("admin:product_color_changelist"),
                    },
                    {
                        "title": _("Теги"),
                        "icon": "tag",
                        "link": reverse_lazy("admin:product_tag_changelist"),
                    },
                    {
                        "title": _("Страны"),
                        "icon": "flag",
                        "link": reverse_lazy("admin:product_country_changelist"),
                    },
                    {
                        "title": _("Пол"),
                        "icon": "wc",
                        "link": reverse_lazy("admin:product_gender_changelist"),
                    },
                ],
            },
            {
                "title": _("Страницы"),
                "icon": "description",
                "collapsible": True,
                "items": [
                    {
                        "title": _("Главная страница"),
                        "icon": "insert_drive_file",
                        "link": reverse_lazy("admin:pages_mainpage_changelist"),
                    },
                    {
                        "title": _("Статические страницы"),
                        "icon": "note_add",
                        "link": reverse_lazy("admin:pages_staticpage_changelist"),
                    },
                    {
                        "title": _("Страница Бонусов"),
                        "icon": "request_page",
                        "link": reverse_lazy("admin:pages_bonuspage_changelist"),
                    },
                    {
                        "title": _("Баннеры"),
                        "icon": "paid",
                        "link": reverse_lazy("admin:pages_banner_changelist"),
                    },
                    {
                        "title": _("Истории"),
                        "icon": "view_carousel",
                        "link": reverse_lazy("admin:pages_stories_changelist"),
                    },
                    {
                        "title": _("Контакты"),
                        "icon": "contact_phone",
                        "link": reverse_lazy("admin:pages_contacts_changelist"),
                    },
                    {
                        "title": _("Способ оплаты"),
                        "icon": "paid",
                        "link": reverse_lazy("admin:pages_methodsofpayment_changelist"),
                    },
                ],
            },
            {
                "title": _("Настройки"),
                "icon": "settings",
                "collapsible": True,
                "items": [
                    {
                        "title": _("Кэшбэк"),
                        "icon": "settings",
                        "link": reverse_lazy("admin:orders_percentcashback_changelist"),
                    },
                    {
                        "title": _("Промо Код"),
                        "icon": "settings",
                        "link": reverse_lazy("admin:orders_promocode_changelist"),
                    },
                ],
            },
        ],
    },
    # "TABS": [
    #     {
    #         "models": [
    #             "app_label.model_name_in_lowercase",
    #         ],
    #         "items": [
    #             {
    #                 "title": _("Your custom title"),
    #                 "link": reverse_lazy("admin:app_label_model_name_changelist"),
    #                 "permission": "sample_app.permission_callback",
    #             },
    #         ],
    #     },
    # ],
}
