from decimal import Decimal

import django_filters

from apps.product.models import Product

from django.db.models import Q, Avg


class ProductFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(field_name='id')
    name = django_filters.CharFilter(method='filter_by_name_or_article')
    country = django_filters.CharFilter(field_name='country__name', lookup_expr='icontains')
    category = django_filters.CharFilter(method='filter_final_category')

    # Фильтрация по полу
    gender = django_filters.CharFilter(method='filter_by_gender')

    # Фильтрация по размеру через запятую
    size = django_filters.CharFilter(method='filter_by_size')

    color = django_filters.CharFilter(method='filter_by_color')

    # Фильтрация по минимальной цене
    price_min = django_filters.NumberFilter(method='filter_by_min_price')

    # Фильтрация по максимальной цене
    price_max = django_filters.NumberFilter(method='filter_by_max_price')

    # Фильтрация по минимальному рейтингу
    rating_min = django_filters.CharFilter(method='filter_by_minimum_rating')  # Изменили на CharFilter для работы с массивом

    class Meta:
        model = Product
        fields = ['id', 'name', 'country', 'category', 'gender', 'size', 'color', 'price_min', 'price_max', 'rating_min']

    def filter_by_name_or_article(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(article__icontains=value))

    def filter_final_category(self, queryset, name, value):
        return queryset.filter(category__name=value, category__subcategories__isnull=True)

    def filter_by_size(self, queryset, name, value):
        size_values = [s.strip() for s in value.split(',')]
        return queryset.filter(product_sizes__size__name__in=size_values).distinct()

    def filter_by_color(self, queryset, name, value):
        color_values = [c.strip() for c in value.split(',')]
        return queryset.filter(product_sizes__color__name__in=color_values).distinct()

    def filter_by_gender(self, queryset, name, value):
        gender_values = [g.strip() for g in value.split(',')]
        return queryset.filter(gender__name__in=gender_values).distinct()

    # Фильтрация по минимальному рейтингу, принимая массив значений через запятую
    def filter_by_minimum_rating(self, queryset, name, value):
        rating_values = [float(r.strip()) for r in value.split(',')]  # Преобразуем строковые значения в float
        min_rating = min(rating_values)  # Находим минимальное значение рейтинга из массива
        return queryset.annotate(average_rating=Avg('product_reviews__rating')).filter(average_rating__gte=min_rating)

    def filter_by_min_price(self, queryset, name, value):
        return queryset.filter(
            Q(discounted_price__gte=value) | (Q(discounted_price__isnull=True) & Q(price__gte=value))
        )

    def filter_by_max_price(self, queryset, name, value):
        return queryset.filter(
            Q(discounted_price__lte=value) | (Q(discounted_price__isnull=True) & Q(price__lte=value))
        )
